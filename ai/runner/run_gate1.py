# ai.runner.run_gate1.py
import json

from db.database import db
from ai.pipeline_router import PipelineRouter
from ai.groq_ai_client import GroqAIClient
from ai.config import (
    GATE1_PROMPT_VERSION,
    GATE1_MODEL,
)
from db.services.posts.processing import (
    get_next_unprocessed_ai,
    mark_ai_processed,
    mark_processed,
)
from db.services.ai_processing.save_result import (
    save_gate1_result,
)


def run_gate1():
    limit = input("Daily request limit for GATE1 (or Enter for no limit): ").strip()
    gate1_ai = GroqAIClient(model=GATE1_MODEL)
    if limit:
        gate1_ai.set_daily_limit(int(limit))

    router = PipelineRouter(gate1_ai=gate1_ai, extraction_ai=None)

    try:
        while True:
            post = get_next_unprocessed_ai()
            if post is None:
                print("No posts remaining.")
                break

            print(f"Processing ID: {post['id']}...")

            try:
                result = router.process_gate1(post)
            except Exception as e:
                if "DAILY_LIMIT_REACHED" in str(e):
                    print(f"Daily limit reached. Stopping.")
                    break
                print(f"ERROR: {e}")
                mark_ai_processed(post["id"])

                continue

            try:
                parsed = json.loads(result["content"])
            except json.JSONDecodeError:
                print("JSON parse error")
                mark_ai_processed(post["id"])
                continue

            tagged_reasoning = (
                f"[model: {router.gate1_ai.model}]\n{result['reasoning']}"
            )

            save_gate1_result(
                post["id"],
                json.dumps(parsed, indent=2, ensure_ascii=False),
                reasoning=tagged_reasoning,
                prompt_version=GATE1_PROMPT_VERSION,
            )
            mark_ai_processed(post["id"])

            if not parsed.get("relevant", False):
                print(f"REJECTED: {parsed.get('reject_reason')}")
                mark_processed(post["id"])
            else:
                result = router.process_extraction(post)
    finally:
        db.close()
