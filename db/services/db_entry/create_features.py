from sqlalchemy import insert

from pydantic import ValidationError


from db.db_supabase import ORG_ID
from db.db_tables import (
    property_features,
)
from db.db_schemas import (
    PropertyFeatureCreate,
)
import logging

logger = logging.getLogger(__name__)


async def create_features(db, property_id: int, post_json: dict, org_id=ORG_ID):
    features = post_json.get("features", [])
    if not features:
        return

    validated = []
    for f in features:
        try:
            validated.append(PropertyFeatureCreate(feature=f))
        except ValidationError:
            logger.warning(f"property_id={property_id} dropped invalid feature={f!r}")

    if not validated:
        return

    await db.execute(
        insert(property_features),
        [
            {"property_id": property_id, "org_id": org_id, "feature": f.feature.value}
            for f in validated
        ],
    )

    print(
        f"insert property_features:\n  property_id: {property_id}\n  count: {len(validated)}"
    )
