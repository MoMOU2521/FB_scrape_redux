# db.db_entry.py
from db.db_supabase import get_session

from db.services.db_entry.resolve_or_create_owner import resolve_or_create_owner
from db.services.db_entry._check_duplicate import _check_duplicate
from db.services.db_entry.create_property_registry import create_property_registry
from db.services.db_entry.create_unit_detail import create_unit_detail
from db.services.db_entry.create_features import create_features
from db.services.db_entry.create_rent_term import create_rent_term
from db.services.db_entry.create_sale_term import create_sale_term
from db.services.db_entry.create_property_note import create_property_note
from db.services.db_entry.resolve_building_id import resolve_building_id
from db.exceptions import (
    OwnerConflictError,
    NoIdentifiableOwnerError,
    BuildingConflictError,
    BuildingNotFoundError,
)

import logging

logger = logging.getLogger(__name__)


async def enter_post(
    post_json: dict,
    author: str,
    post_url: str,
    text: str,
    scraped_at: str,
    building_id: int = None,
):
    async with get_session() as db:
        if building_id is None:
            building_id = await resolve_building_id(db, post_json)

        owner_id = await resolve_or_create_owner(db, post_json, author)

        decision, candidate_property_id = await _check_duplicate(
            db, owner_id, building_id, post_json
        )
        if decision != "insert":
            return decision, candidate_property_id

        property_id = await create_property_registry(db, owner_id, post_json)
        await create_unit_detail(db, property_id, building_id, post_json)
        await create_features(db, property_id, post_json)
        await create_rent_term(db, property_id, post_json, scraped_at)
        await create_sale_term(db, property_id, post_json)
        await create_property_note(db, property_id, post_url, text)

        await db.commit()
        return "insert", property_id
