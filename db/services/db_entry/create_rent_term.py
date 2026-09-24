from sqlalchemy import insert
from datetime import datetime

from db.db_supabase import ORG_ID
from db.db_tables import (
    rent_term,
)
from db.db_schemas import (
    RentTermCreate,
)
import logging

logger = logging.getLogger(__name__)


async def create_rent_term(
    db, property_id: int, post_json: dict, scraped_at: str, org_id=ORG_ID
):
    rent_data = post_json.get("rent_term", {})
    if rent_data.get("rent") is None:
        return

    available = rent_data.get("available")
    if available:
        available_date = datetime.fromisoformat(available).date()
    else:
        available_date = datetime.fromisoformat(scraped_at).date()

    form_data = RentTermCreate(
        rent=rent_data["rent"],
        lease_term=rent_data.get("lease_term"),
        available=available_date,
    )

    # debug = {
    #     "rent_data": rent_data,
    #     "scraped_at": scraped_at,
    #     "available_date": str(available_date),
    #     "model_dump": form_data.model_dump(mode="json"),
    # }

    stmt = insert(rent_term).values(
        property_id=property_id,
        org_id=org_id,
        **form_data.model_dump(),
    )

    # print(
    #     f"insert values: \n{json.dumps(stmt.compile().params, indent=2, default=str)}"
    # )

    await db.execute(stmt)

    # return debug
