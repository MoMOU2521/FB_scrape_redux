from sqlalchemy import insert

from db.db_supabase import ORG_ID
from db.db_tables import (
    sale_term,
)
from db.db_schemas import (
    SaleTermCreate,
)
import logging

logger = logging.getLogger(__name__)


async def create_sale_term(db, property_id: int, post_json: dict, org_id=ORG_ID):
    sale_data = post_json.get("sale_term", {})
    if sale_data.get("price") is None:
        return
    form_data = SaleTermCreate(price=sale_data["price"])
    await db.execute(
        insert(sale_term).values(
            property_id=property_id, org_id=org_id, **form_data.model_dump()
        )
    )

    print(f"insert sale_term:\n  price: {sale_data['price']}")
