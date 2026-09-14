# db.services.db_entry._find_building_id.py
from sqlalchemy import select, func

from db.db_tables import (
    building_registry,
)

import logging

logger = logging.getLogger(__name__)


async def _find_building_id(db, name: str):
    if not name:
        return []
    normalized = name.strip().lower()
    stmt = select(building_registry.c.id).where(
        func.lower(func.trim(building_registry.c.building_name)) == normalized
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]
