# db.services.db_entry.resolve_building_id.py
from db.services.db_entry._find_building_id_by_name import _find_building_id_by_name
from db.services.db_entry._find_building_id_by_alias import _find_building_id_by_alias
from db.exceptions import BuildingConflictError, BuildingNotFoundError

import logging

logger = logging.getLogger(__name__)


async def resolve_building_id(db, post_json: dict) -> int:
    building = post_json.get("building", {})
    standardized = building.get("building_name_standardized")
    raw_name = building.get("building_name")

    matches = await _find_building_id_by_name(db, standardized)
    if not matches:
        matches = await _find_building_id_by_alias(db, standardized)
    if not matches:
        matches = await _find_building_id_by_name(db, raw_name)
    if not matches:
        matches = await _find_building_id_by_alias(db, raw_name)

    if len(matches) > 1:
        raise BuildingConflictError(
            f"{len(matches)} buildings match this post's building name"
        )
    if len(matches) == 0:
        raise BuildingNotFoundError(
            f"no exact building match for '{standardized}' / '{raw_name}'"
        )
    return matches[0]
