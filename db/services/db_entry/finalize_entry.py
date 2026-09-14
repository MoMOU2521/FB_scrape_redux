# db.services.db_entry.finalize_entry.py
from db.database import LocalDatabase
from db.db_entry import (
    enter_post,
)
from db.services.db_entry._queue_for_review import _queue_for_review
from db.exceptions import (
    BuildingNotFoundError,
    OwnerConflictError,
    BuildingConflictError,
    NoIdentifiableOwnerError,
)


async def finalize_entry(row, post_json, building_id=None):
    """
    Single, shared completion point for entering a post into the DB.

    Handles the full decision + error contract in one place so the
    automatic path (process_single_row) and the manual building
    resolution path (attempt_manual_building_resolution) can never
    drift out of sync again:

    - success (insert/discard) -> mark_processed, return True
    - review duplicate         -> queue for review, mark_processed, return True
    - conflict / no owner      -> mark_review_building, return False
    - unexpected error         -> mark_review_building, return False
    """

    try:
        decision, candidate_property_id = await enter_post(
            post_json=post_json,
            author=row["author"],
            post_url=row["post_url"],
            text=row["text"],
            scraped_at=row["scraped_at"],
            building_id=building_id,
        )

    except BuildingNotFoundError:
        # Only possible on the first, automatic attempt (building_id=None).
        # Must propagate untouched so process_single_row can route into
        # attempt_manual_building_resolution — never swallow it here.
        raise

    except (
        OwnerConflictError,
        BuildingConflictError,
        NoIdentifiableOwnerError,
    ) as e:
        print(f"[CONFLICT] row={row['id']} {e}")

        _queue_for_review(row)
        LocalDatabase.mark_processed(row["id"])
        return False

    except Exception as e:
        print(f"[ERROR] row={row['id']} unexpected: {e}")

        LocalDatabase.mark_review_building(row["id"])
        return False

    if decision == "discard":
        print(f"[DISCARD] row={row['id']}")
        LocalDatabase.mark_processed(row["id"])
        return True

    if decision == "review":
        print(f"[REVIEW] row={row['id']} candidate={candidate_property_id}")
        _queue_for_review(row, candidate_property_id)
        LocalDatabase.mark_processed(row["id"])
        return True

    if decision == "insert":
        print(f"[RESOLVED] row={row['id']} -> {row['post_url']}")
        LocalDatabase.mark_processed(row["id"])
        return True

    LocalDatabase.mark_processed(row["id"])
    return False
