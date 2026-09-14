from sqlalchemy import insert


from db.db_supabase import ORG_ID
from db.db_tables import (
    property_note,
)

import logging

logger = logging.getLogger(__name__)


async def create_property_note(
    db, property_id: int, post_url: str, text: str, org_id=ORG_ID
):
    note = f"{post_url}\n<br>\n{text}"
    await db.execute(
        insert(property_note).values(property_id=property_id, org_id=org_id, note=note)
    )
