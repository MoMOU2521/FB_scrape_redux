# db.services.db_entry._find_building_id_by_alias.py
from sqlalchemy import select, func

from db.db_tables import (
    building_alias,
)
import logging

logger = logging.getLogger(__name__)


async def _find_building_id_by_alias(db, name: str):
    if not name:
        return []
    normalized = name.strip().lower()
    stmt = select(building_alias.c.building_id).where(
        func.lower(func.trim(building_alias.c.alias)) == normalized
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]
