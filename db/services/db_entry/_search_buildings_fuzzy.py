# db.services.db_entry._search_buildings_fuzzy.py
from sqlalchemy import select, func

from db.db_tables import (
    building_registry,
)
import logging

logger = logging.getLogger(__name__)


async def _search_buildings_fuzzy(db, name: str, threshold: float = 0.3):
    if not name:
        return []
    similarity_score = func.similarity(building_registry.c.building_name, name)
    stmt = (
        select(
            building_registry.c.id,
            building_registry.c.building_name,
            similarity_score.label("score"),
        )
        .where(similarity_score > threshold)
        .order_by(similarity_score.desc())
        .limit(3)
    )
    result = await db.execute(stmt)
    return result.all()
