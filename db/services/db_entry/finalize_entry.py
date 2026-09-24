# db.services.db_entry.finalize_entry.py
from db.db_entry import (
    enter_post,
)
from db.services.db_entry._queue_for_review import _queue_for_review
from db.services.posts.processing import mark_processed, mark_review_building
from db.exceptions import (
    BuildingNotFoundError,
    OwnerConflictError,
    BuildingConflictError,
    NoIdentifiableOwnerError,
)
from db.services.db_entry.print_entry_summary import print_entry_summary


async def finalize_entry(row, post_json, building_id=None):
    """
    Single, shared completion point for entering a post into the DB.
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
        raise

    except (
        OwnerConflictError,
        BuildingConflictError,
        NoIdentifiableOwnerError,
    ) as e:
        print(f"[CONFLICT] row={row['id']} {e}")

        _queue_for_review(row)
        mark_processed(row["id"])
        return False

    except Exception as e:
        print(f"[ERROR] row={row['id']} unexpected: {e}")

        mark_review_building(row["id"])
        return False

    if decision == "discard":
        print(f"[DISCARD] row={row['id']}")
        mark_processed(row["id"])
        return True

    if decision == "review":
        print(f"[REVIEW] row={row['id']} candidate={candidate_property_id}")
        _queue_for_review(row, candidate_property_id)
        mark_processed(row["id"])
        return True

    # if decision == "insert":
    #     print(f"[RESOLVED] row={row['id']} -> {row['post_url']}")
    #     mark_processed(row["id"])
    #     return True

    if decision == "insert":
        mark_processed(row["id"])
        try:
            await print_entry_summary(row, candidate_property_id)
        except Exception as e:
            print(
                f"[RESOLVED] row={row['id']} property_id={candidate_property_id} "
                f"-> {row['post_url']} (summary failed: {e})"
            )
        return True

    mark_processed(row["id"])
    return False
