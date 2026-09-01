# ai.runner.py
import os
import json
import time
from datetime import datetime, timedelta

from db.db_core import Core
from ai.pipeline_router import PipelineRouter
from ai.groq_ai_client import GroqAIClient
from ai.config import (
    DB_FILE,
    GATE1_PROMPT_VERSION,
    EXTRACTION_PROMPT_VERSION,
    TRANSLITERATE_PROMPT_VERSION,
    GATE1_MODEL,
    EXTRACTION_MODEL,
    TRANSLITERATE_MODEL,
)


class TPMSelfRegulator:
    """Self-regulating TPM (Tokens Per Minute) controller."""

    def __init__(self, max_tokens_per_minute=12000, safety_margin=0.8):
        """
        Args:
            max_tokens_per_minute: Maximum tokens allowed per minute
            safety_margin: Fraction of limit to use (0.8 = 80% of limit)
        """
        self.max_tokens_per_minute = int(max_tokens_per_minute * safety_margin)
        self.window_seconds = 60
        self.token_history = []  # List of (timestamp, tokens_used)
        self.last_request_time = None

    def wait_if_needed(self, estimated_input_tokens=0, estimated_output_tokens=0):
        """
        Check if we need to wait before making a request.
        Returns the wait time in seconds.
        """
        now = time.time()
        total_estimated_tokens = estimated_input_tokens + estimated_output_tokens

        # Clean up old history (older than 60 seconds)
        cutoff = now - self.window_seconds
        self.token_history = [
            (ts, tokens) for ts, tokens in self.token_history if ts > cutoff
        ]

        # Calculate tokens used in the current window
        tokens_used_in_window = sum(tokens for _, tokens in self.token_history)

        # Check if this request would exceed the limit
        if tokens_used_in_window + total_estimated_tokens > self.max_tokens_per_minute:
            # Wait until the oldest token usage falls out of the window
            if self.token_history:
                oldest_ts = min(ts for ts, _ in self.token_history)
                wait_time = (oldest_ts + self.window_seconds) - now + 0.5
                if wait_time > 0:
                    return wait_time

        return 0

    def record_usage(self, input_tokens, output_tokens):
        """Record token usage after a request completes."""
        now = time.time()
        total_tokens = input_tokens + output_tokens
        self.token_history.append((now, total_tokens))
        self.last_request_time = now

        return total_tokens

    def get_usage_stats(self):
        """Get current usage statistics."""
        now = time.time()
        cutoff = now - self.window_seconds
        self.token_history = [
            (ts, tokens) for ts, tokens in self.token_history if ts > cutoff
        ]

        tokens_in_window = sum(tokens for _, tokens in self.token_history)
        requests_in_window = len(self.token_history)

        return {
            "tokens_used_last_minute": tokens_in_window,
            "requests_last_minute": requests_in_window,
            "max_tokens_per_minute": self.max_tokens_per_minute,
            "available_tokens": max(0, self.max_tokens_per_minute - tokens_in_window),
            "remaining_percent": (
                max(0, (1 - tokens_in_window / self.max_tokens_per_minute) * 100)
                if self.max_tokens_per_minute > 0
                else 100
            ),
        }


def run_gate1():
    limit = input("Daily request limit for GATE1 (or Enter for no limit): ").strip()
    gate1_ai = GroqAIClient(model=GATE1_MODEL)
    if limit:
        gate1_ai.set_daily_limit(int(limit))

    print("Opening:", os.path.abspath(DB_FILE))
    db = Core()
    router = PipelineRouter(gate1_ai=gate1_ai, extraction_ai=None)

    try:
        while True:
            post = db.get_next_unprocessed_ai()
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
                db.mark_ai_processed(post["id"])
                # db.mark_processed(post["id"])
                continue

            try:
                parsed = json.loads(result["content"])
            except json.JSONDecodeError:
                print("JSON parse error")
                db.mark_ai_processed(post["id"])
                # db.mark_processed(post["id"])
                continue

            tagged_reasoning = (
                f"[model: {router.gate1_ai.model}]\n{result['reasoning']}"
            )

            db.save_gate1_result(
                post["id"],
                json.dumps(parsed, indent=2, ensure_ascii=False),
                reasoning=tagged_reasoning,
                prompt_version=GATE1_PROMPT_VERSION,
            )
            db.mark_ai_processed(post["id"])

            if not parsed.get("relevant", False):
                print(f"REJECTED: {parsed.get('reject_reason')}")
                db.mark_processed(post["id"])
            else:
                result = router.process_extraction(post)
    finally:
        db.close()


def run_extraction():
    limit = input(
        "Daily request limit for Extraction (or Enter for no limit): "
    ).strip()
    extraction_ai = GroqAIClient(model=EXTRACTION_MODEL)
    if limit:
        extraction_ai.set_daily_limit(int(limit))

    print("Opening:", os.path.abspath(DB_FILE))
    db = Core()
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

            db.save_extraction_result(
                post["id"],
                json.dumps(parsed, indent=2, ensure_ascii=False),
                reasoning=tagged_reasoning,
                prompt_version=EXTRACTION_PROMPT_VERSION,
            )

    finally:
        db.close()


def run_pipeline():
    # --- CLI input for daily limits ---
    gate1_limit = input(
        "Daily request limit for GATE1 (or Enter for no limit): "
    ).strip()
    extraction_limit = input(
        "Daily request limit for Extraction (or Enter for no limit): "
    ).strip()

    gate1_ai = GroqAIClient(model=GATE1_MODEL)
    extraction_ai = GroqAIClient(model=EXTRACTION_MODEL)

    if gate1_limit:
        gate1_ai.set_daily_limit(int(gate1_limit))
    if extraction_limit:
        extraction_ai.set_daily_limit(int(extraction_limit))

    db = Core()
    router = PipelineRouter(gate1_ai=gate1_ai, extraction_ai=extraction_ai)

    # Report counters
    report = {
        "total_processed": 0,
        "gate1_accepted": 0,
        "gate1_rejected": 0,
        "gate1_errors": 0,
        "extraction_accepted": 0,
        "extraction_rejected": 0,
        "extraction_errors": 0,
        "skipped_gate1": 0,
        "rejections": [],  # Store (post_id, stage, reason)
    }

    try:
        while True:
            # Pull next post that hasn't gone through gate1/pipeline yet
            post = db.get_next_unprocessed_ai()
            if post is None:
                print("No posts remaining.")
                break

            print(f"\n{'='*80}")
            print(f"PROCESSING POST ID: {post['id']}")
            print(f"{'='*80}\n")

            # Controls whether this post falls through to extraction after
            # the gate1/routing block below. Only flipped to False on a
            # confirmed gate1 rejection.
            run_extraction_next = True
            post_rejected = False

            if router.should_run_gate1(post):
                # --- Short post: route through gate1 first ---
                print(f"[STEP 1] GATE1 - Analyzing post (short post)")
                print("-" * 40)
                print("[POST TEXT]")
                print(post["text"])
                print("-" * 40)

                try:
                    result = router.process_gate1(post)
                except Exception as e:
                    if "DAILY_LIMIT_REACHED" in str(e):
                        print(
                            f"[STOP] Daily limit reached for GATE1. Stopping pipeline."
                        )
                        break
                    if "Failed after" in str(e):
                        print(
                            f"[STOP] GATE1 exhausted retries (rate limit not clearing): {e}"
                        )
                        report["gate1_errors"] += 1
                        break
                    print(f"[ERROR] GATE1 processing failed: {e}")
                    print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
                    report["gate1_errors"] += 1
                    continue

                if result["reasoning"]:
                    print("[GATE1 REASONING]")
                    print(result["reasoning"])
                    print("-" * 40)

                if result["finish_reason"] != "stop":
                    print(f"[WARNING] GATE1 finish_reason={result['finish_reason']}")

                try:
                    parsed = json.loads(result["content"])
                except json.JSONDecodeError:
                    print(f"[ERROR] GATE1 JSON parse failed")
                    print(f"Raw content: {result['content']}")
                    print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
                    report["gate1_errors"] += 1
                    continue

                # Persist gate1's verdict regardless of accept/reject
                gate1_tagged_reasoning = (
                    f"[model: {router.gate1_ai.model}]\n{result['reasoning']}"
                )
                db.save_gate1_result(
                    post["id"],
                    json.dumps(parsed, indent=2, ensure_ascii=False),
                    reasoning=gate1_tagged_reasoning,
                    prompt_version=GATE1_PROMPT_VERSION,
                )

                if not parsed.get("relevant", False):
                    # Gate1 rejected
                    reject_reason = parsed.get("reject_reason", "No reason provided")
                    print(f"[GATE1 DECISION] REJECTED")
                    print(f"Reason: {reject_reason}")
                    print(
                        f"[ACTION] Post ID {post['id']} marked as processed and rejected."
                    )
                    db.mark_ai_processed(post["id"])
                    db.mark_processed(post["id"])
                    run_extraction_next = False
                    post_rejected = True
                    report["gate1_rejected"] += 1
                    report["rejections"].append(
                        {
                            "post_id": post["id"],
                            "stage": "GATE1",
                            "reason": reject_reason,
                        }
                    )
                else:
                    # Gate1 accepted
                    print(f"[GATE1 DECISION] ACCEPTED")
                    print(
                        f"[ACTION] Post ID {post['id']} passed Gate1, forwarding to Extraction..."
                    )
                    report["gate1_accepted"] += 1
                # else: gate1 accepted — falls through to extraction below
            else:
                # --- Long post: skip straight to extraction ---
                print(f"[STEP 1] SKIPPING GATE1 - Post is too long for Gate1 model")
                print(f"[ACTION] Post ID {post['id']} going directly to Extraction...")
                report["skipped_gate1"] += 1

            if not run_extraction_next:
                print(
                    f"[COMPLETE] Post ID {post['id']} processing finished (rejected at Gate1).\n"
                )
                report["total_processed"] += 1
                continue

            # --- Extraction stage ---
            print(f"\n[STEP 2] EXTRACTION - Analyzing post")
            print("-" * 40)

            try:
                result = router.process_extraction(post)
            except Exception as e:
                if "DAILY_LIMIT_REACHED" in str(e):
                    print(
                        f"[STOP] Daily limit reached for Extraction. Stopping pipeline."
                    )
                    break
                if "Failed after" in str(e):
                    print(
                        f"[STOP] EXTRACTION exhausted retries (rate limit not clearing): {e}"
                    )
                    report["extraction_errors"] += 1
                    break
                print(f"[ERROR] EXTRACTION processing failed: {e}")
                print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
                report["extraction_errors"] += 1
                continue

            if result["reasoning"]:
                print("[EXTRACTION REASONING]")
                print(result["reasoning"])
                print("-" * 40)

            try:
                parsed = json.loads(result["content"])
                print("[EXTRACTION RESULT]")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
                print("-" * 40)
            except json.JSONDecodeError:
                print(f"[ERROR] EXTRACTION JSON parse failed")
                print(f"Raw content: {result['content']}")
                print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
                report["extraction_errors"] += 1
                continue

            if result["finish_reason"] != "stop":
                print(f"[WARNING] EXTRACTION finish_reason={result['finish_reason']}")

            # Persist extraction result
            extraction_tagged_reasoning = (
                f"[model: {router.extraction_ai.model}]\n{result['reasoning']}"
            )
            db.save_extraction_result(
                post["id"],
                json.dumps(parsed, indent=2, ensure_ascii=False),
                reasoning=extraction_tagged_reasoning,
                prompt_version=EXTRACTION_PROMPT_VERSION,
            )
            db.mark_ai_processed(post["id"])

            if not parsed.get("relevant", False):
                reject_reason = parsed.get("reject_reason", "No reason provided")
                print(f"[EXTRACTION DECISION] REJECTED")
                print(f"Reason: {reject_reason}")
                print(f"[ACTION] Post ID {post['id']} marked as rejected.")
                db.mark_processed(post["id"])
                report["extraction_rejected"] += 1
                report["rejections"].append(
                    {
                        "post_id": post["id"],
                        "stage": "EXTRACTION",
                        "reason": reject_reason,
                    }
                )
                post_rejected = True
            else:
                print(f"[EXTRACTION DECISION] ACCEPTED")
                print(
                    f"[ACTION] Post ID {post['id']} successfully processed and accepted."
                )
                report["extraction_accepted"] += 1

            print(f"[COMPLETE] Post ID {post['id']} processing finished.\n")
            report["total_processed"] += 1

    finally:
        db.close()
        print("\n" + "=" * 80)
        print("PIPELINE REPORT")
        print("=" * 80)
        print(f"\nTotal posts processed: {report['total_processed']}")
        print(f"\n--- GATE1 ---")
        print(f"  Accepted: {report['gate1_accepted']}")
        print(f"  Rejected: {report['gate1_rejected']}")
        print(f"  Errors:   {report['gate1_errors']}")
        print(f"  Skipped:  {report['skipped_gate1']} (long posts)")
        print(f"\n--- EXTRACTION ---")
        print(f"  Accepted: {report['extraction_accepted']}")
        print(f"  Rejected: {report['extraction_rejected']}")
        print(f"  Errors:   {report['extraction_errors']}")

        if report["rejections"]:
            print(f"\n--- REJECTIONS ---")
            for r in report["rejections"]:
                print(f"  Post {r['post_id']} rejected at {r['stage']}: {r['reason']}")

        print("\nPipeline finished. Database connection closed.")


# ... TPMSelfRegulator, run_gate1, run_extraction, run_pipeline all unchanged ...


def run_transliterate():
    limit = input(
        "Daily request limit for Transliterate (or Enter for no limit): "
    ).strip()
    transliterate_ai = GroqAIClient(model=TRANSLITERATE_MODEL)
    if limit:
        transliterate_ai.set_daily_limit(int(limit))

    print("Opening:", os.path.abspath(DB_FILE))
    db = Core()
    router = PipelineRouter(
        gate1_ai=None, extraction_ai=None, transliterate_ai=transliterate_ai
    )

    try:
        while True:
            building = db.get_next_unresolved_building()
            if building is None:
                print("No buildings remaining.")
                break

            print(f"Processing post_id: {building['post_id']}...")

            try:
                validated, error = router.process_transliterate(building)
            except Exception as e:
                if "DAILY_LIMIT_REACHED" in str(e):
                    print("Daily limit reached. Stopping.")
                    break
                print(f"ERROR: {e}")
                continue

            if error:
                print(f"PARSE/VALIDATION ERROR: {error}")
                continue

            db.save_transliterate_result(
                building["post_id"],
                validated.model_dump_json(),
                prompt_version=TRANSLITERATE_PROMPT_VERSION,
            )
            print(
                f"Result: {validated.best_guess_name} (confidence={validated.confidence})"
            )

    finally:
        db.close()
