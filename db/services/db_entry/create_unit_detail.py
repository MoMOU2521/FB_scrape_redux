# db.services.db_entry.create_unit_detail.py
from sqlalchemy import insert

from db.db_supabase import ORG_ID
from db.db_tables import (
    condo_apt_unit_info,
)
from db.db_schemas import (
    CAUnitCreate,
    ExposureType,
    ViewType,
)
import logging

logger = logging.getLogger(__name__)


async def create_unit_detail(
    db, property_id: int, building_id: int, post_json: dict, org_id=ORG_ID
):
    unit = post_json.get("unit", {})

    raw_exposure = unit.get("exposure")
    try:
        exposure = ExposureType(raw_exposure) if raw_exposure is not None else None
    except ValueError:
        logger.warning(
            f"property_id={property_id} dropped invalid exposure={raw_exposure!r}"
        )
        exposure = None

    raw_view = unit.get("view")
    try:
        view = ViewType(raw_view) if raw_view is not None else None
    except ValueError:
        logger.warning(f"property_id={property_id} dropped invalid view={raw_view!r}")
        view = None

    form_data = CAUnitCreate(
        building_id=building_id,
        room_number=unit.get("room_number"),
        floor=unit.get("floor"),
        tower=unit.get("tower"),
        bedroom=unit.get("bedroom") if unit.get("bedroom") is not None else 1,
        bathroom=unit.get("bathroom") if unit.get("bathroom") is not None else 1,
        sqm=unit.get("sqm"),
        exposure=exposure,
        view=view,
    )  # room_number/floor/tower/bedroom/bathroom/sqm raise normally on violation

    await db.execute(
        insert(condo_apt_unit_info).values(
            property_id=property_id, org_id=org_id, **form_data.model_dump()
        )
    )

    # print(
    #     f"insert condo_apt_unit_info:\n"
    #     # f"  property_id: {property_id}\n"
    #     f"  building_id: {building_id}\n"
    #     f"  room_number: {unit.get('room_number')}\n"
    #     f"  floor: {unit.get('floor')}\n"
    #     f"  tower: {unit.get('tower')}\n"
    #     f"  bedroom: {unit.get('bedroom') if unit.get('bedroom') is not None else 1}\n"
    #     f"  bathroom: {unit.get('bathroom') if unit.get('bathroom') is not None else 1}\n"
    #     f"  sqm: {unit.get('sqm')}\n"
    #     f"  exposure: {exposure}\n"
    #     f"  view: {view}"
    # )
