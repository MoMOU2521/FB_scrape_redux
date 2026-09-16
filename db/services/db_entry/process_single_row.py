# db.services.db_entry.process_single_row.py
import json

from db.services.posts.processing import mark_processed
from db.exceptions import (
    BuildingNotFoundError,
)
from db.services.db_entry.finalize_entry import finalize_entry
from db.services.db_entry.attempt_manual_building_resolution import (
    attempt_manual_building_resolution,
)


async def process_single_row(row, transliterate_ai, db):
    """
    Process one extraction result into production DB.
    """

    try:
        post_json = json.loads(row["extraction_result_json"])

    except (json.JSONDecodeError, TypeError) as e:
        print(f"[SKIP] row={row['id']} invalid JSON: {e}")

        mark_processed(row["id"])
        return False

    try:
        return await finalize_entry(row, post_json, building_id=None)

    except BuildingNotFoundError:
        return await attempt_manual_building_resolution(
            row,
            post_json,
            transliterate_ai,
        )
