# db._search_owners_duplicate.py
from sqlalchemy import select

from db.db_tables import (
    owner_registry,
    owner_contact,
)

import logging

logger = logging.getLogger(__name__)


async def _search_owners_duplicate(db, contact_values: list[str]):
    if not contact_values:
        return []

    stmt = (
        select(owner_registry.c.id, owner_registry.c.name, owner_registry.c.registered)
        .distinct()
        .select_from(
            owner_registry.join(
                owner_contact, owner_contact.c.owner_id == owner_registry.c.id
            )
        )
        .where(owner_contact.c.contact_value.in_(contact_values))
        .order_by(owner_registry.c.registered.desc())
    )
    result = await db.execute(stmt)
    return result.mappings().all()
