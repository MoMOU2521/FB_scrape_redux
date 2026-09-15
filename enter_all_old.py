# # enter_all.py
# import asyncio
# import json
# from datetime import datetime, timezone

# from ai import transliterate_pipeline
# from ai.config import TRANSLITERATE_MODEL
# from ai.groq_ai_client import GroqAIClient

# from db.db_core import core
# from db.db_entry import (
#     enter_post,
#     resolve_building_candidates,
#     _search_buildings_fuzzy,
#     BuildingNotFoundError,
#     OwnerConflictError,
#     BuildingConflictError,
#     NoIdentifiableOwnerError,
# )

# from db.db_supabase import get_session
# from web.building_alias import add_building_alias

# def build_building_candidates(post_json):
#     """
#     Collect building names already available from extraction.
#     Does not call AI.
#     """
#     building = post_json.get("building", {})

#     candidates = []

#     for source, name in [
#         ("original", building.get("building_name")),
#         ("standardized", building.get("building_name_standardized")),
#     ]:
#         if name:
#             name = name.strip()

#             if name and name not in [c["name"] for c in candidates]:
#                 candidates.append(
#                     {
#                         "source": source,
#                         "name": name,
#                     }
#                 )

#     return candidates


# def _queue_for_review(row, candidate_property_id=None):
#     core.cur.execute(
#         """
#         INSERT INTO entry_review_queue
#         (
#             post_id,
#             candidate_property_id,
#             reviewed,
#             created_at
#         )
#         VALUES (?, ?, 0, ?)
#         """,
#         (
#             row["id"],
#             candidate_property_id,
#             datetime.now(timezone.utc).isoformat(),
#         ),
#     )
#     core.conn.commit()


# async def finalize_entry(row, post_json, building_id=None):
#     """
#     Single, shared completion point for entering a post into the DB.

#     Handles the full decision + error contract in one place so the
#     automatic path (process_single_row) and the manual building
#     resolution path (attempt_manual_building_resolution) can never
#     drift out of sync again:

#     - success (insert/discard) -> mark_processed, return True
#     - review duplicate         -> queue for review, mark_processed, return True
#     - conflict / no owner      -> mark_review_building, return False
#     - unexpected error         -> mark_review_building, return False
#     """

#     try:
#         decision, candidate_property_id = await enter_post(
#             post_json=post_json,
#             author=row["author"],
#             post_url=row["post_url"],
#             text=row["text"],
#             scraped_at=row["scraped_at"],
#             building_id=building_id,
#         )

#     except BuildingNotFoundError:
#         # Only possible on the first, automatic attempt (building_id=None).
#         # Must propagate untouched so process_single_row can route into
#         # attempt_manual_building_resolution — never swallow it here.
#         raise

#     except (
#         OwnerConflictError,
#         BuildingConflictError,
#         NoIdentifiableOwnerError,
#     ) as e:
#         print(f"[CONFLICT] row={row['id']} {e}")

#         _queue_for_review(row)
#         core.mark_processed(row["id"])
#         return False

#     except Exception as e:
#         print(f"[ERROR] row={row['id']} unexpected: {e}")

#         core.mark_review_building(row["id"])
#         return False

#     if decision == "discard":
#         print(f"[DISCARD] row={row['id']}")
#         core.mark_processed(row["id"])
#         return True

#     if decision == "review":
#         print(f"[REVIEW] row={row['id']} candidate={candidate_property_id}")
#         _queue_for_review(row, candidate_property_id)
#         core.mark_processed(row["id"])
#         return True

#     if decision == "insert":
#         print(f"[RESOLVED] row={row['id']} -> {row['post_url']}")
#         core.mark_processed(row["id"])
#         return True

#     core.mark_processed(row["id"])
#     return False


# async def attempt_manual_building_resolution(row, post_json, transliterate_ai):
#     """
#     Building recovery pipeline:

#     1. Try original + standardized exact matches
#     2. Generate AI transliteration candidate
#     3. Try all candidates exact match
#     4. Fuzzy search
#     5. User confirmation
#     6. Alias handling
#     7. Enter DB
#     """

#     candidates = build_building_candidates(post_json)

#     # --------------------------------------------------------
#     # Stage 1: deterministic lookup
#     # --------------------------------------------------------
#     async with get_session() as db:
#         result = await resolve_building_candidates(
#             db,
#             [c["name"] for c in candidates],
#         )

#     if result:
#         building_id, matched_name = result

#         print(f"[EXACT MATCH] row={row['id']} name='{matched_name}'")

#         return await finalize_entry(row, post_json, building_id=building_id)

#     # --------------------------------------------------------
#     # Stage 2: AI transliteration
#     # --------------------------------------------------------
#     validated, error = transliterate_pipeline.run_processing(
#         transliterate_ai,
#         row["text"],
#     )

#     print(
#         "[TRANSLITERATE RESULT]"
#         f"\nbest_guess: \n{getattr(validated, 'best_guess_name', None) if validated else None}"
#     )

#     if not error and validated and validated.best_guess_name:
#         ai_name = validated.best_guess_name.strip()

#         if ai_name and ai_name not in [c["name"] for c in candidates]:
#             candidates.append(
#                 {
#                     "source": "transliteration",
#                     "name": ai_name,
#                 }
#             )

#     if not candidates:
#         print(f"[NO_USABLE_NAME] row={row['id']}")

#         core.mark_review_building(row["id"])
#         return False

#     # --------------------------------------------------------
#     # Stage 3: deterministic lookup again
#     # --------------------------------------------------------
#     async with get_session() as db:
#         result = await resolve_building_candidates(
#             db,
#             [c["name"] for c in candidates],
#         )

#     if result:
#         building_id, matched_name = result

#         print(f"[EXACT MATCH] row={row['id']} name='{matched_name}'")

#         return await finalize_entry(row, post_json, building_id=building_id)

#     # --------------------------------------------------------
#     # Stage 4: select fuzzy search name
#     # --------------------------------------------------------
#     if len(candidates) == 1:
#         search_name = candidates[0]["name"]

#     else:
#         print("\n[BUILDING NAME OPTIONS]")

#         for i, c in enumerate(candidates, start=1):
#             print(f"  {i}. {c['source']}: {c['name']}")

#         choice = input(f"Select search name (1-{len(candidates)}): ").strip()

#         if choice not in [str(i) for i in range(1, len(candidates) + 1)]:
#             core.mark_review_building(row["id"])
#             return False

#         search_name = candidates[int(choice) - 1]["name"]

#     # --------------------------------------------------------
#     # Stage 5: fuzzy search
#     # --------------------------------------------------------
#     async with get_session() as db:
#         fuzzy_candidates = await _search_buildings_fuzzy(
#             db,
#             search_name,
#         )

#     if not fuzzy_candidates:
#         print(f"[NO_CANDIDATES] \nrow={row['id']} " f"search_name='{search_name}'")

#         core.mark_review_building(row["id"])
#         return False

#     print(f"\n[BUILDING MATCH]\nrow={row['id']}\n" f"search_name='{search_name}'")

#     for i, c in enumerate(fuzzy_candidates, start=1):
#         print(f"  {i}. id={c.id} " f"name='{c.building_name}' " f"score={c.score:.3f}")

#     print("  0. None of these — send to manual review")

#     choice = input(f"Select match (0-{len(fuzzy_candidates)}): ").strip()

#     if choice == "0" or choice not in [
#         str(i) for i in range(1, len(fuzzy_candidates) + 1)
#     ]:
#         core.mark_review_building(row["id"])
#         return False

#     picked = fuzzy_candidates[int(choice) - 1]

#     # --------------------------------------------------------
#     # Stage 6: alias
#     # --------------------------------------------------------
#     # Exact fuzzy match means no alias needed.
#     # The selected building name is already the canonical name.
#     if round(picked.score, 3) != 1.000:

#         alias_candidates = [
#             c["name"]
#             for c in candidates
#             if c["name"].lower() != picked.building_name.lower()
#         ]

#         if alias_candidates:
#             print("\n[ALIAS OPTIONS]")

#             for i, alias in enumerate(alias_candidates, start=1):
#                 print(f"  {i}. {alias}")

#             print("  0. No alias")

#             alias_choice = input(
#                 f"Select alias to save (0-{len(alias_candidates)}): "
#             ).strip()

#             if alias_choice in [str(i) for i in range(1, len(alias_candidates) + 1)]:
#                 await add_building_alias(
#                     picked.id,
#                     alias_candidates[int(alias_choice) - 1],
#                 )

#     return await finalize_entry(row, post_json, building_id=picked.id)


# async def process_single_row(row, transliterate_ai):
#     """
#     Process one extraction result into production DB.
#     """

#     try:
#         post_json = json.loads(row["extraction_result_json"])

#     except (json.JSONDecodeError, TypeError) as e:
#         print(f"[SKIP] row={row['id']} invalid JSON: {e}")

#         core.mark_processed(row["id"])
#         return False

#     try:
#         return await finalize_entry(row, post_json, building_id=None)

#     except BuildingNotFoundError:
#         return await attempt_manual_building_resolution(
#             row,
#             post_json,
#             transliterate_ai,
#         )


async def main():
    # Fetch all unprocessed posts with extraction data
    rows = core.cur.execute("""
        SELECT id,
               author,
               post_url,
               text,
               scraped_at,
               extraction_result_json
        FROM posts
        WHERE processed = 0
          AND extraction_result_json IS NOT NULL
          AND extraction_result_json != ''
        ORDER BY id
        """).fetchall()

    if not rows:
        print("No posts to process.")
        return

    # AI only needed for building resolution fallback
    transliterate_ai = GroqAIClient(model=TRANSLITERATE_MODEL)

    success = 0
    failed = 0

    for row in rows:
        print(f"\n========Processing ID: {row['id']}========")

        result = await process_single_row(
            row,
            transliterate_ai,
        )

        if result:
            success += 1
        else:
            failed += 1

    print(f"\nDone. success={success} failed={failed}")


if __name__ == "__main__":
    asyncio.run(main())
