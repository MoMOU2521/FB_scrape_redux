# db.services.db_entry._get_owner_contacts.py
from sqlalchemy import select

from db.db_tables import (
    owner_contact,
)

import logging

logger = logging.getLogger(__name__)


async def _get_owner_contacts(db, owner_id: int) -> set[str]:
    stmt = select(owner_contact.c.contact_value).where(
        owner_contact.c.owner_id == owner_id
    )
    result = await db.execute(stmt)
    return {row[0] for row in result.all()}
