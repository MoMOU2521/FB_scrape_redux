# db.services.db_entry.print_entry_summary.py
from sqlalchemy import select

from db.db_supabase import get_session
from db.db_tables import (
    property_registry,
    owner_registry,
    owner_contact,
    condo_apt_unit_info,
    building_registry,
    property_features,
    rent_term,
    sale_term,
)


def _v(x):
    return "-" if x is None or x == "" else x


async def print_entry_summary(row, property_id: int) -> None:
    async with get_session() as db:
        head = (
            (
                await db.execute(
                    select(
                        property_registry.c.owner_id,
                        property_registry.c.for_rent,
                        property_registry.c.for_sale,
                        property_registry.c.verification_status,
                        owner_registry.c.name.label("owner_name"),
                        condo_apt_unit_info.c.building_id,
                        building_registry.c.building_name,
                        condo_apt_unit_info.c.room_number,
                        condo_apt_unit_info.c.floor,
                        condo_apt_unit_info.c.tower,
                        condo_apt_unit_info.c.bedroom,
                        condo_apt_unit_info.c.bathroom,
                        condo_apt_unit_info.c.sqm,
                        condo_apt_unit_info.c.exposure,
                        condo_apt_unit_info.c.view,
                    )
                    .select_from(
                        property_registry.outerjoin(
                            owner_registry,
                            owner_registry.c.id == property_registry.c.owner_id,
                        )
                        .outerjoin(
                            condo_apt_unit_info,
                            condo_apt_unit_info.c.property_id == property_registry.c.id,
                        )
                        .outerjoin(
                            building_registry,
                            building_registry.c.id == condo_apt_unit_info.c.building_id,
                        )
                    )
                    .where(property_registry.c.id == property_id)
                )
            )
            .mappings()
            .one()
        )

        contacts = (
            await db.execute(
                select(
                    owner_contact.c.contact_type, owner_contact.c.contact_value
                ).where(owner_contact.c.owner_id == head["owner_id"])
            )
        ).all()

        features = (
            (
                await db.execute(
                    select(property_features.c.feature).where(
                        property_features.c.property_id == property_id
                    )
                )
            )
            .scalars()
            .all()
        )

        rent = (
            (
                await db.execute(
                    select(rent_term).where(rent_term.c.property_id == property_id)
                )
            )
            .mappings()
            .first()
        )
        sale = (
            (
                await db.execute(
                    select(sale_term).where(sale_term.c.property_id == property_id)
                )
            )
            .mappings()
            .first()
        )

    h = head

    def line(label, value):
        print(f"  {label:<10}: {_v(value)}")

    print(f"[RESOLVED] row={row['id']} property_id={property_id}")
    line("url", row["post_url"])
    print()
    line("owner", f"#{h['owner_id']} {_v(h['owner_name'])}")
    for t, v in contacts:
        line(f"  {t}", v)
    print()
    line("building", f"#{h['building_id']} {_v(h['building_name'])}")
    line("bedroom", h["bedroom"])
    line("bathroom", h["bathroom"])
    line("sqm", h["sqm"])
    line("floor", h["floor"])
    line("tower", h["tower"])
    line("room", h["room_number"])
    line("exposure", h["exposure"])
    line("view", h["view"])
    line("features", ", ".join(features))
    print()
    line("listing", h["verification_status"])
    if rent:
        line("rent", rent["rent"])
        line("lease", rent["lease_term"])
        line("available", rent["available"])
    if sale:
        line("sale", sale["price"])
    print()
