# # ai.runner.run_pipeline.py
# import json

# from db.database import LocalDatabase
# from ai.pipeline_router import PipelineRouter
# from ai.groq_ai_client import GroqAIClient
# from ai.config import (
#     GATE1_PROMPT_VERSION,
#     EXTRACTION_PROMPT_VERSION,
#     GATE1_MODEL,
#     EXTRACTION_MODEL,
# )
# from db.services.posts.processing import (
#     get_next_unprocessed_ai,
#     mark_ai_processed,
# )
# from db.services.ai_processing.save_result import (
#     save_gate1_result,
#     save_extraction_result,
# )
# from db.services.posts.processing import mark_processed


# def run_pipeline():
#     # --- CLI input for daily limits ---
#     gate1_limit = input(
#         "Daily request limit for GATE1 (or Enter for no limit): "
#     ).strip()
#     extraction_limit = input(
#         "Daily request limit for Extraction (or Enter for no limit): "
#     ).strip()

#     gate1_ai = GroqAIClient(model=GATE1_MODEL)
#     extraction_ai = GroqAIClient(model=EXTRACTION_MODEL)

#     if gate1_limit:
#         gate1_ai.set_daily_limit(int(gate1_limit))
#     if extraction_limit:
#         extraction_ai.set_daily_limit(int(extraction_limit))

#     router = PipelineRouter(gate1_ai=gate1_ai, extraction_ai=extraction_ai)

#     # Report counters
#     report = {
#         "total_processed": 0,
#         "gate1_accepted": 0,
#         "gate1_rejected": 0,
#         "gate1_errors": 0,
#         "extraction_accepted": 0,
#         "extraction_rejected": 0,
#         "extraction_errors": 0,
#         "skipped_gate1": 0,
#         "rejections": [],  # Store (post_id, stage, reason)
#     }

#     try:
#         while True:
#             # Pull next post that hasn't gone through gate1/pipeline yet
#             post = get_next_unprocessed_ai()
#             if post is None:
#                 print("No posts remaining.")
#                 break

#             print(f"\n{'='*80}")
#             print(f"PROCESSING POST ID: {post['id']}")
#             print(f"{'='*80}\n")

#             # Controls whether this post falls through to extraction after
#             # the gate1/routing block below. Only flipped to False on a
#             # confirmed gate1 rejection.
#             run_extraction_next = True
#             post_rejected = False

#             if router.should_run_gate1(post):
#                 # --- Short post: route through gate1 first ---
#                 print(f"[STEP 1] GATE1 - Analyzing post (short post)")
#                 print("-" * 40)
#                 print("[POST TEXT]")
#                 print(post["text"])
#                 print("-" * 40)

#                 try:
#                     result = router.process_gate1(post)
#                 except Exception as e:
#                     if "DAILY_LIMIT_REACHED" in str(e):
#                         print(
#                             f"[STOP] Daily limit reached for GATE1. Stopping pipeline."
#                         )
#                         break
#                     if "Failed after" in str(e):
#                         print(
#                             f"[STOP] GATE1 exhausted retries (rate limit not clearing): {e}"
#                         )
#                         report["gate1_errors"] += 1
#                         break
#                     print(f"[ERROR] GATE1 processing failed: {e}")
#                     print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
#                     report["gate1_errors"] += 1
#                     continue

#                 if result["reasoning"]:
#                     print("[GATE1 REASONING]")
#                     print(result["reasoning"])
#                     print("-" * 40)

#                 if result["finish_reason"] != "stop":
#                     print(f"[WARNING] GATE1 finish_reason={result['finish_reason']}")

#                 try:
#                     parsed = json.loads(result["content"])
#                 except json.JSONDecodeError:
#                     print(f"[ERROR] GATE1 JSON parse failed")
#                     print(f"Raw content: {result['content']}")
#                     print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
#                     report["gate1_errors"] += 1
#                     continue

#                 # Persist gate1's verdict regardless of accept/reject
#                 gate1_tagged_reasoning = (
#                     f"[model: {router.gate1_ai.model}]\n{result['reasoning']}"
#                 )
#                 save_gate1_result(
#                     post["id"],
#                     json.dumps(parsed, indent=2, ensure_ascii=False),
#                     reasoning=gate1_tagged_reasoning,
#                     prompt_version=GATE1_PROMPT_VERSION,
#                 )

#                 if not parsed.get("relevant", False):
#                     # Gate1 rejected
#                     reject_reason = parsed.get("reject_reason", "No reason provided")
#                     print(f"[GATE1 DECISION] REJECTED")
#                     print(f"Reason: {reject_reason}")
#                     print(
#                         f"[ACTION] Post ID {post['id']} marked as processed and rejected."
#                     )
#                     mark_ai_processed(post["id"])
#                     mark_processed(post["id"])
#                     run_extraction_next = False
#                     post_rejected = True
#                     report["gate1_rejected"] += 1
#                     report["rejections"].append(
#                         {
#                             "post_id": post["id"],
#                             "stage": "GATE1",
#                             "reason": reject_reason,
#                         }
#                     )
#                 else:
#                     # Gate1 accepted
#                     print(f"[GATE1 DECISION] ACCEPTED")
#                     print(
#                         f"[ACTION] Post ID {post['id']} passed Gate1, forwarding to Extraction..."
#                     )
#                     report["gate1_accepted"] += 1
#                 # else: gate1 accepted — falls through to extraction below
#             else:
#                 # --- Long post: skip straight to extraction ---
#                 print(f"[STEP 1] SKIPPING GATE1 - Post is too long for Gate1 model")
#                 print(f"[ACTION] Post ID {post['id']} going directly to Extraction...")
#                 report["skipped_gate1"] += 1

#             if not run_extraction_next:
#                 print(
#                     f"[COMPLETE] Post ID {post['id']} processing finished (rejected at Gate1).\n"
#                 )
#                 report["total_processed"] += 1
#                 continue

#             # --- Extraction stage ---
#             print(f"\n[STEP 2] EXTRACTION - Analyzing post")
#             print("-" * 40)

#             try:
#                 result = router.process_extraction(post)
#             except Exception as e:
#                 if "DAILY_LIMIT_REACHED" in str(e):
#                     print(
#                         f"[STOP] Daily limit reached for Extraction. Stopping pipeline."
#                     )
#                     break
#                 if "Failed after" in str(e):
#                     print(
#                         f"[STOP] EXTRACTION exhausted retries (rate limit not clearing): {e}"
#                     )
#                     report["extraction_errors"] += 1
#                     break
#                 print(f"[ERROR] EXTRACTION processing failed: {e}")
#                 print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
#                 report["extraction_errors"] += 1
#                 continue

#             if result["reasoning"]:
#                 print("[EXTRACTION REASONING]")
#                 print(result["reasoning"])
#                 print("-" * 40)

#             try:
#                 parsed = json.loads(result["content"])
#                 print("[EXTRACTION RESULT]")
#                 print(json.dumps(parsed, indent=2, ensure_ascii=False))
#                 print("-" * 40)
#             except json.JSONDecodeError:
#                 print(f"[ERROR] EXTRACTION JSON parse failed")
#                 print(f"Raw content: {result['content']}")
#                 print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
#                 report["extraction_errors"] += 1
#                 continue

#             if result["finish_reason"] != "stop":
#                 print(f"[WARNING] EXTRACTION finish_reason={result['finish_reason']}")

#             # Persist extraction result
#             extraction_tagged_reasoning = (
#                 f"[model: {router.extraction_ai.model}]\n{result['reasoning']}"
#             )
#             save_extraction_result(
#                 post["id"],
#                 json.dumps(parsed, indent=2, ensure_ascii=False),
#                 reasoning=extraction_tagged_reasoning,
#                 prompt_version=EXTRACTION_PROMPT_VERSION,
#             )
#             mark_ai_processed(post["id"])

#             if not parsed.get("relevant", False):
#                 reject_reason = parsed.get("reject_reason", "No reason provided")
#                 print(f"[EXTRACTION DECISION] REJECTED")
#                 print(f"Reason: {reject_reason}")
#                 print(f"[ACTION] Post ID {post['id']} marked as rejected.")
#                 mark_processed(post["id"])
#                 report["extraction_rejected"] += 1
#                 report["rejections"].append(
#                     {
#                         "post_id": post["id"],
#                         "stage": "EXTRACTION",
#                         "reason": reject_reason,
#                     }
#                 )
#                 post_rejected = True
#             else:
#                 print(f"[EXTRACTION DECISION] ACCEPTED")
#                 print(
#                     f"[ACTION] Post ID {post['id']} successfully processed and accepted."
#                 )
#                 report["extraction_accepted"] += 1

#             print(f"[COMPLETE] Post ID {post['id']} processing finished.\n")
#             report["total_processed"] += 1

#     finally:
#         print("\n" + "=" * 80)
#         print("PIPELINE REPORT")
#         print("=" * 80)
#         print(f"\nTotal posts processed: {report['total_processed']}")
#         print(f"\n--- GATE1 ---")
#         print(f"  Accepted: {report['gate1_accepted']}")
#         print(f"  Rejected: {report['gate1_rejected']}")
#         print(f"  Errors:   {report['gate1_errors']}")
#         print(f"  Skipped:  {report['skipped_gate1']} (long posts)")
#         print(f"\n--- EXTRACTION ---")
#         print(f"  Accepted: {report['extraction_accepted']}")
#         print(f"  Rejected: {report['extraction_rejected']}")
#         print(f"  Errors:   {report['extraction_errors']}")

#         if report["rejections"]:
#             print(f"\n--- REJECTIONS ---")
#             for r in report["rejections"]:
#                 print(f"  Post {r['post_id']} rejected at {r['stage']}: {r['reason']}")

#         print("\nPipeline finished. Database connection closed.")
# ai.runner.run_pipeline.py
import json

from ai.pipeline_router import PipelineRouter
from ai.groq_ai_client import GroqAIClient
from ai.config import (
    GATE1_MODEL,
    GATE2_MODEL,
    EXTRACTION_MODEL,
    GATE1_PROMPT_VERSION,
    GATE2_PROMPT_VERSION,
    EXTRACTION_PROMPT_VERSION,
)
from db.services.posts.processing import (
    get_next_unprocessed_ai,
    mark_ai_processed,
    mark_processed,
)
from db.services.ai_processing.save_result import (
    save_gate1_result,
    save_gate2_result,
    save_extraction_result,
)


def _run_gate1(router, post, report):
    print("[STEP 1] GATE1 - Analyzing post")
    print("-" * 40)
    print("[POST TEXT]")
    print(post["text"])
    print("-" * 40)

    try:
        result = router.process_gate1(post)
    except Exception as e:
        msg = str(e)

        if "DAILY_LIMIT_REACHED" in msg:
            print("[STOP] Daily limit reached for GATE1. Stopping pipeline.")
            raise

        if "Failed after" in msg:
            print(f"[STOP] GATE1 exhausted retries (rate limit not clearing): {msg}")
            report["gate1_errors"] += 1
            raise

        print(f"[ERROR] GATE1 processing failed: {msg}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["gate1_errors"] += 1
        return None

    if result["reasoning"]:
        print("[GATE1 REASONING]")
        print(result["reasoning"])
        print("-" * 40)

    if result["finish_reason"] != "stop":
        print(f"[WARNING] GATE1 finish_reason={result['finish_reason']}")

    try:
        parsed = json.loads(result["content"])
    except (json.JSONDecodeError, TypeError):
        print("[ERROR] GATE1 JSON parse failed")
        print(f"Raw content: {result['content']}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["gate1_errors"] += 1
        return None

    gate1_tagged_reasoning = (
        f"[model: {router.gate1_ai.model}]\n" f"{result['reasoning'] or ''}"
    )

    save_gate1_result(
        post["id"],
        json.dumps(parsed, indent=2, ensure_ascii=False),
        reasoning=gate1_tagged_reasoning,
        prompt_version=GATE1_PROMPT_VERSION,
    )

    if not parsed.get("relevant", False):
        reject_reason = parsed.get("reject_reason", "No reason provided")

        print("[GATE1 DECISION] REJECTED")
        print(f"Reason: {reject_reason}")
        print(f"[ACTION] Post ID {post['id']} marked as processed and rejected.")

        mark_ai_processed(post["id"])
        mark_processed(post["id"])

        report["gate1_rejected"] += 1
        report["rejections"].append(
            {"post_id": post["id"], "stage": "GATE1", "reason": reject_reason}
        )
        return False

    print("[GATE1 DECISION] ACCEPTED")
    print(f"[ACTION] Post ID {post['id']} passed Gate1, forwarding to Gate2...")

    report["gate1_accepted"] += 1
    return True


def _run_gate2(router, post, report):
    print("\n[STEP 2] GATE2 - Analyzing post")
    print("-" * 40)

    try:
        result = router.process_gate2(post)
    except Exception as e:
        msg = str(e)

        if "DAILY_LIMIT_REACHED" in msg:
            print("[STOP] Daily limit reached for GATE2. Stopping pipeline.")
            raise

        if "Failed after" in msg:
            print(f"[STOP] GATE2 exhausted retries (rate limit not clearing): {msg}")
            report["gate2_errors"] += 1
            raise

        print(f"[ERROR] GATE2 processing failed: {msg}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["gate2_errors"] += 1
        return None

    if result["reasoning"]:
        print("[GATE2 REASONING]")
        print(result["reasoning"])
        print("-" * 40)

    if result["finish_reason"] != "stop":
        print(f"[WARNING] GATE2 finish_reason={result['finish_reason']}")

    try:
        parsed = json.loads(result["content"])
    except (json.JSONDecodeError, TypeError):
        print("[ERROR] GATE2 JSON parse failed")
        print(f"Raw content: {result['content']}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["gate2_errors"] += 1
        return None

    gate2_tagged_reasoning = (
        f"[model: {router.gate2_ai.model}]\n" f"{result['reasoning'] or ''}"
    )

    save_gate2_result(
        post["id"],
        json.dumps(parsed, indent=2, ensure_ascii=False),
        reasoning=gate2_tagged_reasoning,
        prompt_version=GATE2_PROMPT_VERSION,
    )

    if not parsed.get("relevant", False):
        reject_reason = parsed.get("reject_reason", "No reason provided")

        print("[GATE2 DECISION] REJECTED")
        print(f"Reason: {reject_reason}")
        print(f"[ACTION] Post ID {post['id']} marked as processed and rejected.")

        mark_ai_processed(post["id"])
        mark_processed(post["id"])

        report["gate2_rejected"] += 1
        report["rejections"].append(
            {"post_id": post["id"], "stage": "GATE2", "reason": reject_reason}
        )
        return False

    print("[GATE2 DECISION] ACCEPTED")
    print(f"[ACTION] Post ID {post['id']} passed Gate2, forwarding to Extraction...")

    report["gate2_accepted"] += 1
    return True


def _run_extraction(router, post, report):
    print("\n[STEP 3] EXTRACTION - Analyzing post")
    print("-" * 40)

    try:
        result = router.process_extraction(post)
    except Exception as e:
        msg = str(e)

        if "DAILY_LIMIT_REACHED" in msg:
            print("[STOP] Daily limit reached for Extraction. Stopping pipeline.")
            raise

        if "Failed after" in msg:
            print(
                "[STOP] EXTRACTION exhausted retries "
                f"(rate limit not clearing): {msg}"
            )
            report["extraction_errors"] += 1
            raise

        print(f"[ERROR] EXTRACTION processing failed: {msg}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["extraction_errors"] += 1
        return None

    if result["reasoning"]:
        print("[EXTRACTION REASONING]")
        print(result["reasoning"])
        print("-" * 40)

    try:
        parsed = json.loads(result["content"])
        print("[EXTRACTION RESULT]")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        print("-" * 40)
    except (json.JSONDecodeError, TypeError):
        print("[ERROR] EXTRACTION JSON parse failed")
        print(f"Raw content: {result['content']}")
        print(f"[ACTION] Post ID {post['id']} will be retried on next run.")
        report["extraction_errors"] += 1
        return None

    if result["finish_reason"] != "stop":
        print(f"[WARNING] EXTRACTION finish_reason=" f"{result['finish_reason']}")

    extraction_tagged_reasoning = (
        f"[model: {router.extraction_ai.model}]\n" f"{result['reasoning'] or ''}"
    )

    save_extraction_result(
        post["id"],
        json.dumps(parsed, indent=2, ensure_ascii=False),
        reasoning=extraction_tagged_reasoning,
        prompt_version=EXTRACTION_PROMPT_VERSION,
    )

    mark_ai_processed(post["id"])

    if not parsed.get("relevant", False):
        reject_reason = parsed.get("reject_reason", "No reason provided")

        print("[EXTRACTION DECISION] REJECTED")
        print(f"Reason: {reject_reason}")
        print(f"[ACTION] Post ID {post['id']} marked as rejected.")

        mark_processed(post["id"])

        report["extraction_rejected"] += 1
        report["rejections"].append(
            {"post_id": post["id"], "stage": "EXTRACTION", "reason": reject_reason}
        )
        return False

    print("[EXTRACTION DECISION] ACCEPTED")
    print(f"[ACTION] Post ID {post['id']} successfully processed and accepted.")

    report["extraction_accepted"] += 1
    return True


def run_pipeline():
    # --- CLI input for daily limit (one process, one limit) ---
    daily_limit = input("Daily request limit (or Enter for no limit): ").strip()

    gate1_ai = GroqAIClient(model=GATE1_MODEL)
    gate2_ai = GroqAIClient(model=GATE2_MODEL)
    extraction_ai = GroqAIClient(model=EXTRACTION_MODEL)

    if daily_limit:
        for client in (gate1_ai, gate2_ai, extraction_ai):
            client.set_daily_limit(int(daily_limit))

    router = PipelineRouter(
        gate1_ai=gate1_ai,
        gate2_ai=gate2_ai,
        extraction_ai=extraction_ai,
    )

    report = {
        "total_processed": 0,
        "gate1_accepted": 0,
        "gate1_rejected": 0,
        "gate1_errors": 0,
        "gate2_accepted": 0,
        "gate2_rejected": 0,
        "gate2_errors": 0,
        "extraction_accepted": 0,
        "extraction_rejected": 0,
        "extraction_errors": 0,
        "rejections": [],
    }

    try:
        while True:
            post = get_next_unprocessed_ai()

            if post is None:
                print("No posts remaining.")
                break

            print(f"\n{'=' * 80}")
            print(f"PROCESSING POST ID: {post['id']}")
            print(f"{'=' * 80}\n")

            try:
                # --- Gate 1 ---
                gate1_result = _run_gate1(router, post, report)

                if gate1_result is None:
                    # Ordinary Gate1 error. Post remains available for next run.
                    continue

                if gate1_result is False:
                    print(
                        f"[COMPLETE] Post ID {post['id']} processing "
                        "finished (rejected at Gate1).\n"
                    )
                    report["total_processed"] += 1
                    continue

                # --- Gate 2 ---
                gate2_result = _run_gate2(router, post, report)

                if gate2_result is None:
                    # Ordinary Gate2 error. Post remains available for next run.
                    continue

                if gate2_result is False:
                    print(
                        f"[COMPLETE] Post ID {post['id']} processing "
                        "finished (rejected at Gate2).\n"
                    )
                    report["total_processed"] += 1
                    continue

                # --- Extraction ---
                extraction_result = _run_extraction(router, post, report)

                if extraction_result is None:
                    # Ordinary extraction error. Post remains available for next run.
                    continue

                print(f"[COMPLETE] Post ID {post['id']} processing finished.\n")
                report["total_processed"] += 1

            except Exception as e:
                msg = str(e)

                if "DAILY_LIMIT_REACHED" in msg:
                    print("[STOP] Daily limit reached. Stopping pipeline.")
                    break

                if "Failed after" in msg:
                    print(f"[STOP] Retries exhausted: {msg}")
                    break

                print(f"[ERROR] Post {post['id']}: {msg}")

                # Stage handlers already count ordinary processing errors.
                # This catches unexpected errors outside those handlers.
                report["gate1_errors"] += 1
                continue

    finally:
        print("\n" + "=" * 80)
        print("PIPELINE REPORT")
        print("=" * 80)

        print(f"\nTotal posts processed: {report['total_processed']}")

        print("\n--- GATE1 ---")
        print(f"  Accepted: {report['gate1_accepted']}")
        print(f"  Rejected: {report['gate1_rejected']}")
        print(f"  Errors:   {report['gate1_errors']}")

        print("\n--- GATE2 ---")
        print(f"  Accepted: {report['gate2_accepted']}")
        print(f"  Rejected: {report['gate2_rejected']}")
        print(f"  Errors:   {report['gate2_errors']}")

        print("\n--- EXTRACTION ---")
        print(f"  Accepted: {report['extraction_accepted']}")
        print(f"  Rejected: {report['extraction_rejected']}")
        print(f"  Errors:   {report['extraction_errors']}")

        if report["rejections"]:
            print("\n--- REJECTIONS ---")

            for rejection in report["rejections"]:
                print(
                    f"  Post {rejection['post_id']} "
                    f"rejected at {rejection['stage']}: "
                    f"{rejection['reason']}"
                )

        print("\nPipeline finished. Database connection closed.")
