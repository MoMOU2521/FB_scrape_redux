# db.services.db_entry.resolve_building_candidates.py
from db.services.db_entry._find_building_id_by_name import _find_building_id_by_name
from db.services.db_entry._find_building_id_by_alias import _find_building_id_by_alias

from db.exceptions import BuildingConflictError

import logging

logger = logging.getLogger(__name__)


async def resolve_building_candidates(db, names: list[str]):
    """
    Try resolving multiple building name candidates.

    Order:
    - exact canonical building name
    - exact building alias

    Returns:
        (building_id, matched_name)
        or None

    Raises:
        BuildingConflictError if a name matches multiple buildings.
    """

    for name in names:
        if not name:
            continue

        name = name.strip()

        # Canonical name
        matches = await _find_building_id_by_name(
            db,
            name,
        )

        if len(matches) > 1:
            raise BuildingConflictError(f"{len(matches)} buildings match name '{name}'")

        if len(matches) == 1:
            return matches[0], name

        # Alias
        matches = await _find_building_id_by_alias(
            db,
            name,
        )

        if len(matches) > 1:
            raise BuildingConflictError(
                f"{len(matches)} buildings match alias '{name}'"
            )

        if len(matches) == 1:
            return matches[0], name

    return None
