# ai.runner.run_extraction.py
import os
import json
import time

from db.database import LocalDatabase
from ai.pipeline_router import PipelineRouter
from ai.groq_ai_client import GroqAIClient
from ai.config import (
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_MODEL,
)

from db.services.ai_processing.save_result import (
    save_extraction_result,
)


def run_extraction():
    limit = input(
        "Daily request limit for Extraction (or Enter for no limit): "
    ).strip()
    extraction_ai = GroqAIClient(model=EXTRACTION_MODEL)
    if limit:
        extraction_ai.set_daily_limit(int(limit))

    router = PipelineRouter(gate1_ai=None, extraction_ai=extraction_ai)

    # TPM tracking
    MAX_TPM = 12000
    token_window = []  # (timestamp, tokens_used)
    WINDOW_SECONDS = 60

    try:
        while True:
            post = db.get_next_unprocessed_for_extraction()
            if post is None:
                print("No posts available for extraction.")
                break

            print("=" * 80)
            print(f"ID: {post['id']}")
            print(f"Author: {post['author']}")
            print(f"Group: {post['group_name']}")
            print(f"Timestamp: {post['timestamp']}")
            print(f"URL: {post['post_url']}")
            print("-" * 80)
            print(post["text"])
            print("=" * 80)

            # --- TPM Self-Regulation ---
            now = time.time()
            # Remove old entries
            token_window = [
                (ts, tokens) for ts, tokens in token_window if now - ts < WINDOW_SECONDS
            ]

            # Estimate tokens for this request
            estimated_tokens = len(post["text"]) // 4 + 1000

            # Check if we'd exceed TPM
            current_usage = sum(tokens for _, tokens in token_window)
            if current_usage + estimated_tokens > MAX_TPM:
                if token_window:
                    oldest_ts = min(ts for ts, _ in token_window)
                    wait_time = (oldest_ts + WINDOW_SECONDS) - now + 0.5
                    if wait_time > 0:
                        print(f"TPM limit approaching. Waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        # Reset window after waiting
                        token_window = []
                        now = time.time()

            try:
                result = router.process_extraction(post)
            except Exception as e:
                if "DAILY_LIMIT_REACHED" in str(e):
                    print("Daily limit reached. Stopping.")
                    break
                print(f"ERROR: {e}")
                continue

            # Record token usage (estimated since we don't have actual)
            token_window.append((now, estimated_tokens))

            if result["reasoning"]:
                print("--- EXTRACTION REASONING ---")
                print(result["reasoning"])
                print("----------------------------")

            try:
                parsed = json.loads(result["content"])
                print("EXTRACTION RESULT:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"PARSE ERROR: {result['content']}")
                continue

            if result["finish_reason"] != "stop":
                print(f"WARNING: finish_reason={result['finish_reason']}")

            tagged_reasoning = (
                f"[model: {router.extraction_ai.model}]\n{result['reasoning']}"
            )

            save_extraction_result(
                db,
                post["id"],
                json.dumps(parsed, indent=2, ensure_ascii=False),
                reasoning=tagged_reasoning,
                prompt_version=EXTRACTION_PROMPT_VERSION,
            )

    finally:
        db.close()
