# db.services.db_entry._check_duplicate.py
from decimal import Decimal
from sqlalchemy import select


from db.db_tables import (
    property_registry,
    condo_apt_unit_info,
)

import logging

logger = logging.getLogger(__name__)


async def _check_duplicate(db, owner_id: int, building_id: int, post_json: dict) -> str:
    unit = post_json.get("unit", {})
    room_number = unit.get("room_number")
    floor = unit.get("floor")
    sqm = unit.get("sqm")
    tower = unit.get("tower")

    stmt = (
        select(
            condo_apt_unit_info.c.property_id,
            condo_apt_unit_info.c.room_number,
            condo_apt_unit_info.c.floor,
            condo_apt_unit_info.c.sqm,
            condo_apt_unit_info.c.tower,
        )
        .select_from(
            property_registry.join(
                condo_apt_unit_info,
                condo_apt_unit_info.c.property_id == property_registry.c.id,
            )
        )
        .where(
            property_registry.c.owner_id == owner_id,
            condo_apt_unit_info.c.building_id == building_id,
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return "insert", None

    incoming_sqm = Decimal(str(sqm)) if sqm is not None else None

    for r in rows:
        # Certain duplicate — exact room number match
        if (
            room_number is not None
            and r.room_number is not None
            and room_number == r.room_number
        ):
            return "discard", r.property_id

        # Possible duplicate — floor + sqm match.
        # Tower is only a disqualifier when BOTH sides have a real,
        # differing value. Null/null (common — no tower info at all)
        # must NOT block the match.
        tower_conflicts = tower is not None and r.tower is not None and tower != r.tower

        sqm_match = (
            incoming_sqm is not None and r.sqm is not None and incoming_sqm == r.sqm
        )

        if (
            floor is not None
            and r.floor is not None
            and floor == r.floor
            and sqm_match
            and not tower_conflicts
        ):
            return "review", r.property_id

    return "insert", None
