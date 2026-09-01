# db_entry.py
#
# Orchestration for the manual "Enter into DB" button.
# Uses SQLAlchemy Core against db_tables.py — no ORM, no relationship
# traversal. Pydantic (db_schemas.py) validates input shape before any
# SQL is built. Postgres constraints + RLS are the final enforcement layer.

import re
from decimal import Decimal
from sqlalchemy import select, insert, or_, func
from datetime import datetime, date, timezone
from pydantic import ValidationError
import json

from db.db_supabase import get_session, ORG_ID
from db.db_tables import (
    owner_registry,
    owner_contact,
    property_registry,
    condo_apt_unit_info,
    property_features,
    rent_term,
    sale_term,
    building_registry,
    building_alias,
    property_note,
)
from db.db_schemas import (
    OwnerRegistryCreate,
    OwnerContactCreate,
    PropertyRegistryCreate,
    VerificationStatus,
    CAUnitCreate,
    PropertyFeatureCreate,
    RentTermCreate,
    SaleTermCreate,
    ExposureType,
    ViewType,
)
import logging

logger = logging.getLogger(__name__)


class OwnerConflictError(Exception):
    """2+ existing owners match this post's contacts."""

    pass


class NoIdentifiableOwnerError(Exception):
    """Author unusable and no contact provides a name."""

    pass


class BuildingConflictError(Exception):
    """2+ existing buildings match this post's building name."""

    pass


class BuildingNotFoundError(Exception):
    """No exact building match found — building lookup/creation is out of
    scope for this pipeline, so this post cannot proceed."""

    pass


# ============================================================
# OWNER
# ============================================================


def normalize_phone_th(raw: str) -> str:
    """Normalize Thai phone numbers to local format: 0XXXXXXXXX."""
    if not raw:
        return raw

    s = re.sub(r"[\s\-()]", "", raw.strip())

    if s.startswith("+66"):
        s = s[3:]
    elif s.startswith("66"):
        s = s[2:]

    if not s.startswith("0"):
        s = "0" + s

    return s


# async def _add_owner_contact(db, owner_id: int, contact_value: str):
#     normalized = normalize_phone_th(contact_value)
#     stmt = insert(owner_contact).values(
#         owner_id=owner_id,
#         contact_value=normalized,
#     )
#     await db.execute(stmt)


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


async def _get_owner_contacts(db, owner_id: int) -> set[str]:
    stmt = select(owner_contact.c.contact_value).where(
        owner_contact.c.owner_id == owner_id
    )
    result = await db.execute(stmt)
    return {row[0] for row in result.all()}


def _resolve_owner_name(author: str, contacts: list[dict]):
    if author and author != "Anonymous":
        return author
    if contacts:
        first = contacts[0]
        if first.get("contact_name"):
            return first["contact_name"]
        if first.get("contact_value"):
            return first["contact_value"]
    return None


def _build_contact_list(gate1_contacts: list[dict], author: str) -> list[dict]:
    contacts = list(gate1_contacts)
    if author and author != "Anonymous":
        contacts.append(
            {
                "contact_name": None,
                "contact_type": "facebook",
                "contact_value": author,
                "contact_note": None,
            }
        )
    return contacts


# contact validation error get omit and pass
async def resolve_or_create_owner(
    db, post_json: dict, author: str, org_id=ORG_ID
) -> int:
    gate1_contacts = post_json.get("owner", {}).get("contacts", [])
    all_contacts_raw = _build_contact_list(gate1_contacts, author)

    validated_contacts = []

    for c in all_contacts_raw:
        try:
            # Normalize only phone-type contacts
            contact_type = c.get("contact_type", "")
            if contact_type in ("phone", "line", "whatsapp", "telephone", "call"):
                c["contact_value"] = normalize_phone_th(c["contact_value"])
            validated_contacts.append(OwnerContactCreate(**c))
        except ValidationError:
            logger.warning("dropped invalid contact: %r", c)

    name = _resolve_owner_name(author, gate1_contacts)

    if not validated_contacts and not name:
        raise NoIdentifiableOwnerError(
            "author is unusable and no valid contact provides a name"
        )

    contact_values = [c.contact_value for c in validated_contacts]

    matches = await _search_owners_duplicate(db, contact_values)

    if len(matches) > 1:
        raise OwnerConflictError(
            f"{len(matches)} existing owners match this post's contacts"
        )

    if len(matches) == 1:
        owner_id = matches[0]["id"]

        existing_values = await _get_owner_contacts(db, owner_id)

        new_contacts = [
            c for c in validated_contacts if c.contact_value not in existing_values
        ]

        if new_contacts:
            await db.execute(
                insert(owner_contact),
                [
                    {
                        "owner_id": owner_id,
                        "org_id": org_id,
                        "contact_name": c.contact_name,
                        "contact_type": c.contact_type.value,
                        "contact_value": c.contact_value,
                        "contact_note": c.contact_note,
                    }
                    for c in new_contacts
                ],
            )
            print(
                f"insert owner_contacts:\n  owner_id: {owner_id}\n  count: {len(new_contacts)}"
            )

        return owner_id

    result = await db.execute(
        insert(owner_registry)
        .values(
            org_id=org_id,
            name=name,
        )
        .returning(owner_registry.c.id)
    )
    owner_id = result.scalar_one()

    print(f"insert owner:\n  id: {owner_id}\n  name: {name}")

    if validated_contacts:
        await db.execute(
            insert(owner_contact),
            [
                {
                    "owner_id": owner_id,
                    "org_id": org_id,
                    "contact_name": c.contact_name,
                    "contact_type": c.contact_type.value,
                    "contact_value": c.contact_value,
                    "contact_note": c.contact_note,
                }
                for c in validated_contacts
            ],
        )
        print(
            f"insert owner_contacts:\n  owner_id: {owner_id}\n  count: {len(validated_contacts)}"
        )

    return owner_id


# ============================================================
# BUILDING (lookup only — never creates)
# ============================================================


async def _find_building_id(db, name: str):
    if not name:
        return []
    normalized = name.strip().lower()
    stmt = select(building_registry.c.id).where(
        func.lower(func.trim(building_registry.c.building_name)) == normalized
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def _find_building_id_by_name(db, name: str):
    if not name:
        return []
    normalized = name.strip().lower()
    stmt = select(building_registry.c.id).where(
        func.lower(func.trim(building_registry.c.building_name)) == normalized
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def _find_building_id_by_alias(db, name: str):
    if not name:
        return []
    normalized = name.strip().lower()
    stmt = select(building_alias.c.building_id).where(
        func.lower(func.trim(building_alias.c.alias)) == normalized
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def resolve_building_candidates(db, names: list[str]):
    """
    Try resolving multiple building name candidates.

    Order:
    - exact canonical building name
    - exact building alias

    Returns:
        (building_id, matched_name)
        or None

    Raises:
        BuildingConflictError if a name matches multiple buildings.
    """

    for name in names:
        if not name:
            continue

        name = name.strip()

        # Canonical name
        matches = await _find_building_id_by_name(
            db,
            name,
        )

        if len(matches) > 1:
            raise BuildingConflictError(f"{len(matches)} buildings match name '{name}'")

        if len(matches) == 1:
            return matches[0], name

        # Alias
        matches = await _find_building_id_by_alias(
            db,
            name,
        )

        if len(matches) > 1:
            raise BuildingConflictError(
                f"{len(matches)} buildings match alias '{name}'"
            )

        if len(matches) == 1:
            return matches[0], name

    return None


# CLAUDE: SHAKY ADD
async def _search_buildings_fuzzy(db, name: str, threshold: float = 0.3):
    if not name:
        return []
    similarity_score = func.similarity(building_registry.c.building_name, name)
    stmt = (
        select(
            building_registry.c.id,
            building_registry.c.building_name,
            similarity_score.label("score"),
        )
        .where(similarity_score > threshold)
        .order_by(similarity_score.desc())
        .limit(3)
    )
    result = await db.execute(stmt)
    return result.all()


async def resolve_building_id(db, post_json: dict) -> int:
    building = post_json.get("building", {})
    standardized = building.get("building_name_standardized")
    raw_name = building.get("building_name")

    matches = await _find_building_id_by_name(db, standardized)
    if not matches:
        matches = await _find_building_id_by_alias(db, standardized)
    if not matches:
        matches = await _find_building_id_by_name(db, raw_name)
    if not matches:
        matches = await _find_building_id_by_alias(db, raw_name)

    # matches_by_name = await _find_building_id_by_name(db, standardized)
    # matches_by_alias = await _find_building_id_by_alias(db, standardized)
    # matches_by_name_raw = await _find_building_id_by_name(db, raw_name)
    # matches_by_alias_raw = await _find_building_id_by_alias(db, raw_name)

    # print(f"Matches for standardized '{standardized}': {matches_by_name}")
    # print(f"Alias matches for '{standardized}': {matches_by_alias}")
    # print(f"Matches for raw '{raw_name}': {matches_by_name_raw}")
    # print(f"Alias matches for '{raw_name}': {matches_by_alias_raw}")

    if len(matches) > 1:
        raise BuildingConflictError(
            f"{len(matches)} buildings match this post's building name"
        )
    if len(matches) == 0:
        raise BuildingNotFoundError(
            f"no exact building match for '{standardized}' / '{raw_name}'"
        )
    return matches[0]


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


# ============================================================
# CHECK DUPLICATE PROPERTY
# ============================================================


async def _check_duplicate(db, owner_id: int, building_id: int, post_json: dict) -> str:
    unit = post_json.get("unit", {})
    room_number = unit.get("room_number")
    floor = unit.get("floor")
    sqm = unit.get("sqm")
    tower = unit.get("tower")

    stmt = (
        select(
            condo_apt_unit_info.c.property_id,
            condo_apt_unit_info.c.room_number,
            condo_apt_unit_info.c.floor,
            condo_apt_unit_info.c.sqm,
            condo_apt_unit_info.c.tower,
        )
        .select_from(
            property_registry.join(
                condo_apt_unit_info,
                condo_apt_unit_info.c.property_id == property_registry.c.id,
            )
        )
        .where(
            property_registry.c.owner_id == owner_id,
            condo_apt_unit_info.c.building_id == building_id,
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return "insert", None

    incoming_sqm = Decimal(str(sqm)) if sqm is not None else None

    for r in rows:
        # Certain duplicate — exact room number match
        if (
            room_number is not None
            and r.room_number is not None
            and room_number == r.room_number
        ):
            return "discard", r.property_id

        # Possible duplicate — floor + sqm match.
        # Tower is only a disqualifier when BOTH sides have a real,
        # differing value. Null/null (common — no tower info at all)
        # must NOT block the match.
        tower_conflicts = tower is not None and r.tower is not None and tower != r.tower

        sqm_match = (
            incoming_sqm is not None and r.sqm is not None and incoming_sqm == r.sqm
        )

        if (
            floor is not None
            and r.floor is not None
            and floor == r.floor
            and sqm_match
            and not tower_conflicts
        ):
            return "review", r.property_id

    return "insert", None


# ============================================================
# PROPERTY REGISTRY
# ============================================================


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
        .values(owner_id=owner_id, org_id=org_id, **form_data.model_dump())
        .returning(property_registry.c.id)
    )
    property_id = result.scalar_one()
    print(f"insert property_registry:\n  id: {property_id}\n  owner_id: {owner_id}")
    return property_id


# ============================================================
# UNIT DETAIL
# ============================================================


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

    print(
        f"insert condo_apt_unit_info:\n"
        # f"  property_id: {property_id}\n"
        f"  building_id: {building_id}\n"
        f"  room_number: {unit.get('room_number')}\n"
        f"  floor: {unit.get('floor')}\n"
        f"  tower: {unit.get('tower')}\n"
        f"  bedroom: {unit.get('bedroom') if unit.get('bedroom') is not None else 1}\n"
        f"  bathroom: {unit.get('bathroom') if unit.get('bathroom') is not None else 1}\n"
        f"  sqm: {unit.get('sqm')}\n"
        f"  exposure: {exposure}\n"
        f"  view: {view}"
    )


# ============================================================
# FEATURES
# ============================================================


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


# ============================================================
# RENT / SALE TERM
# ============================================================


async def create_rent_term(
    db, property_id: int, post_json: dict, scraped_at: str, org_id=ORG_ID
):
    rent_data = post_json.get("rent_term", {})
    if rent_data.get("rent") is None:
        return

    # print("rent_data:", rent_data)
    # print("scraped_at:", scraped_at)

    available = rent_data.get("available")
    if available:
        available_date = datetime.fromisoformat(available).date()
    else:
        available_date = datetime.fromisoformat(scraped_at).date()

    # print("available_date:", available_date)

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

    # print("model_dump:", form_data.model_dump())

    stmt = insert(rent_term).values(
        property_id=property_id,
        org_id=org_id,
        **form_data.model_dump(),
    )

    # print("insert values:", stmt.compile().params)
    print(
        f"insert values: \n{json.dumps(stmt.compile().params, indent=2, default=str)}"
    )

    await db.execute(stmt)

    # return debug


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


# ============================================================
# PROPERTY'S NOTE
# ============================================================


async def create_property_note(
    db, property_id: int, post_url: str, text: str, org_id=ORG_ID
):
    note = f"{post_url}\n<br>\n{text}"
    await db.execute(
        insert(property_note).values(property_id=property_id, org_id=org_id, note=note)
    )


# ============================================================
# ORCHESTRATION
# ============================================================


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
