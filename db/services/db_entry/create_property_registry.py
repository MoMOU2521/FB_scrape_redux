# db.services.db_entry.create_property_registry.py
from sqlalchemy import insert

from db.db_supabase import ORG_ID
from db.db_tables import property_registry
from db.db_schemas import (
    PropertyRegistryCreate,
    VerificationStatus,
)
import logging

logger = logging.getLogger(__name__)


async def create_property_registry(
    db, owner_id: int, post_json: dict, org_id=ORG_ID
) -> int:
    form_data = PropertyRegistryCreate(
        for_sale=post_json.get("for_sale") or False,
        for_rent=post_json.get("for_rent") or False,
        verification_status=VerificationStatus(post_json["verification_status"]),
    )

    result = await db.execute(
        insert(property_registry)
        .values(
            owner_id=owner_id,
            org_id=org_id,
            fb_posted=False,
            **form_data.model_dump(),
        )
        .returning(property_registry.c.id)
    )
    property_id = result.scalar_one()
    # print(f"insert property_registry:\n  id: {property_id}\n  owner_id: {owner_id}")
    return property_id
