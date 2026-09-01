# db_tables.py
#
# SQLAlchemy Core table skeletons — structural mirror only.
# No ORM classes, no relationships, no Base, no cascade behavior.
# Column shapes copied by hand from the main app's models.py.
# Source of truth is that repo — keep in sync manually.

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Boolean,
    SmallInteger,
    Numeric,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

metadata = MetaData()


# ----------------------------
# Enum types — created elsewhere by main app's migrations.
# create_type=False so we never try to (re)create them here.
# ----------------------------
contact_type_enum = Enum(
    "email",
    "phone",
    "facebook",
    "line_id",
    "whatsapp",
    "other",
    name="contact_type",
    create_type=False,
)

verification_status_enum = Enum(
    "unverified",
    "open",
    # NOTE: only two values ever seen in gate1 output. Real enum may have
    # more members (e.g. verified/rejected) — not confirmed against DB.
    name="verification_status",
    create_type=False,
)

exposure_enum = Enum(
    "north",
    "south",
    "east",
    "west",
    "northeast",
    "northwest",
    "southeast",
    "southwest",
    name="exposure",
    create_type=False,
)

view_type_enum = Enum(
    "city",
    "river",
    "park",
    "garden",
    "pool",
    name="view_type",
    create_type=False,
)

feature_type_enum = Enum(
    "pet_allowed",
    "unfurnished",
    "washer",
    "dryer",
    "oven",
    "bathtub",
    "open_bedroom",
    "loft_bed",
    "walk_in_closet",
    "closed_kitchen",
    "extra_kitchen",
    "maidroom",
    "multi_use_room",
    "corner_unit",
    "duplex",
    "terrace",
    "penthouse",
    "pool_villa",
    name="feature_type",
    create_type=False,
)

# sale_term_type_enum intentionally NOT declared — SaleTermType members
# never seen, gate1 never produces this field, column never written to.


# ----------------------------
# Tables
# ----------------------------

owner_registry = Table(
    "owner_registry",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("registered", DateTime(timezone=True)),
    Column("name", String(100), nullable=True),
)

owner_contact = Table(
    "owner_contact",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("owner_id", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True)),
    Column("contact_name", String(100), nullable=True),
    Column("contact_type", contact_type_enum, nullable=False),
    Column("contact_value", String(100), nullable=False),
    Column("contact_note", String(50), nullable=True),
)

verification_status_enum = Enum(
    "unverified",
    "open",
    "verified",
    name="verification_status",
    create_type=False,
)

property_registry = Table(
    "property_registry",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("owner_id", Integer, nullable=False),
    Column("for_sale", Boolean, nullable=False),
    Column("for_rent", Boolean, nullable=False),
    Column("date_listed", DateTime(timezone=True)),
    Column("verification_status", verification_status_enum, nullable=False),
    Column("fb_posted", Boolean, nullable=True),  # left null always, see above
)

condo_apt_unit_info = Table(
    "condo_apt_unit_info",
    metadata,
    Column("property_id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("building_id", Integer, nullable=False),
    Column("room_number", String(25), nullable=True),
    Column("floor", String(10), nullable=True),
    Column("tower", String(10), nullable=True),
    Column("bedroom", SmallInteger, nullable=True),
    Column("bathroom", SmallInteger, nullable=True),
    Column("sqm", Numeric(precision=7, scale=2), nullable=True),
    Column("exposure", exposure_enum, nullable=True),
    Column("view", view_type_enum, nullable=True),
)

property_features = Table(
    "property_features",
    metadata,
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("property_id", Integer, primary_key=True, nullable=False),
    Column("feature", feature_type_enum, primary_key=True, nullable=False),
)

rent_term = Table(
    "rent_term",
    metadata,
    Column("property_id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("rent", Integer, nullable=False),
    Column("lease_term", SmallInteger, nullable=True),
    Column("available", Date, nullable=True),
)

sale_term = Table(
    "sale_term",
    metadata,
    Column("property_id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column("price", Integer, nullable=False),
    # sale_term_type NOT declared — see note above.
)

# ----------------------------
# building_registry — minimal, READ-ONLY use (lookup only, never inserted to)
# Only columns actually seen/used: id, building_name
# ----------------------------
building_registry = Table(
    "building_registry",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("building_name", String),  # exact length/type not confirmed
)

building_alias = Table(
    "building_alias",
    metadata,
    Column("building_id", Integer, nullable=False),
    Column("alias", String, nullable=False),
)
# RETARD AI BULLSHIT HERE? CLEAN IT UP LATER
property_note = Table(
    "property_note",
    metadata,
    Column("property_id", Integer, primary_key=True),
    Column("org_id", PG_UUID(as_uuid=True), nullable=True),
    Column(
        "note", String, nullable=False
    ),  # actual type is Text, String works for insert
)
