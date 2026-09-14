# db.services.db_entry.enter_post_with_known_building.py
from db.services.db_entry._check_duplicate import _check_duplicate
from db.services.db_entry.create_property_registry import create_property_registry
from db.services.db_entry.create_unit_detail import create_unit_detail
from db.services.db_entry.create_features import create_features
from db.services.db_entry.create_rent_term import create_rent_term
from db.services.db_entry.create_sale_term import create_sale_term
from db.services.db_entry.create_property_note import create_property_note

import logging

logger = logging.getLogger(__name__)


async def enter_post_with_known_building(
    db,
    post_json: dict,
    owner_id: int,
    building_id: int,
    post_url: str,
    text: str,
    scraped_at: str,
):
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
