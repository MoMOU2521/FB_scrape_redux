# ai/listing_schema.py

FEATURE_ENUM = [
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
]

VIEW_ENUM = ["city", "river", "park", "garden", "pool"]
EXPOSURE_ENUM = [
    "north",
    "south",
    "east",
    "west",
    "northeast",
    "northwest",
    "southeast",
    "southwest",
]
CONTACT_TYPE_ENUM = ["email", "phone", "facebook", "line_id", "whatsapp", "other"]

LISTING_SCHEMA = {
    "type": "object",
    "properties": {
        "relevant": {"type": "boolean"},
        "reject_reason": {"type": ["string", "null"]},
        "verification_status": {"type": "string", "enum": ["unverified", "open"]},
        "for_rent": {"type": ["boolean", "null"]},
        "for_sale": {"type": ["boolean", "null"]},
        "owner": {
            "type": "object",
            "properties": {
                "contacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "contact_name": {"type": ["string", "null"]},
                            "contact_type": {
                                "type": "string",
                                "enum": CONTACT_TYPE_ENUM,
                            },
                            "contact_value": {"type": "string"},
                        },
                        "required": ["contact_name", "contact_type", "contact_value"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["contacts"],
            "additionalProperties": False,
        },
        "building": {
            "type": "object",
            "properties": {
                "building_name": {"type": ["string", "null"]},
                "building_name_standardized": {"type": ["string", "null"]},
            },
            "required": ["building_name", "building_name_standardized"],
            "additionalProperties": False,
        },
        "unit": {
            "type": "object",
            "properties": {
                "room_number": {"type": ["string", "null"]},
                "floor": {"type": ["string", "null"]},
                "tower": {"type": ["string", "null"]},
                "bedroom": {"type": ["integer", "null"]},
                "bathroom": {"type": ["integer", "null"]},
                "sqm": {"type": ["number", "null"]},
                "view": {"type": ["string", "null"], "enum": VIEW_ENUM + [None]},
                "exposure": {
                    "type": ["string", "null"],
                    "enum": EXPOSURE_ENUM + [None],
                },
            },
            "required": [
                "room_number",
                "floor",
                "tower",
                "bedroom",
                "bathroom",
                "sqm",
                "view",
                "exposure",
            ],
            "additionalProperties": False,
        },
        "features": {
            "type": "array",
            "items": {"type": "string", "enum": FEATURE_ENUM},
        },
        "rent_term": {
            "type": "object",
            "properties": {
                "rent": {"type": ["integer", "null"]},
                "lease_term": {"type": ["integer", "null"]},
                "available": {"type": ["string", "null"]},
            },
            "required": ["rent", "lease_term", "available"],
            "additionalProperties": False,
        },
        "sale_term": {
            "type": "object",
            "properties": {"price": {"type": ["integer", "null"]}},
            "required": ["price"],
            "additionalProperties": False,
        },
    },
    "required": [
        "relevant",
        "reject_reason",
        "verification_status",
        "for_rent",
        "for_sale",
        "owner",
        "building",
        "unit",
        "features",
        "rent_term",
        "sale_term",
    ],
    "additionalProperties": False,
}


# ---- Pydantic backstop (still required — qwen is best-effort, not strict) ----

from pydantic import BaseModel, field_validator
from typing import Optional, List


class Contact(BaseModel):
    contact_name: Optional[str] = None
    contact_type: str
    contact_value: str

    @field_validator("contact_type")
    @classmethod
    def check_contact_type(cls, v):
        if v not in CONTACT_TYPE_ENUM:
            raise ValueError(f"invalid contact_type: {v}")
        return v


class Owner(BaseModel):
    contacts: List[Contact] = []


class Building(BaseModel):
    building_name: Optional[str] = None
    building_name_standardized: Optional[str] = None


class Unit(BaseModel):
    room_number: Optional[str] = None
    floor: Optional[str] = None
    tower: Optional[str] = None
    bedroom: Optional[int] = None
    bathroom: Optional[int] = None
    sqm: Optional[float] = None
    view: Optional[str] = None
    exposure: Optional[str] = None

    @field_validator("bathroom")
    @classmethod
    def default_bathroom(cls, v):
        # your rule: assume 1 if omitted, on condo/apartment listings
        return v if v is not None else 1

    @field_validator("view")
    @classmethod
    def check_view(cls, v):
        if v is not None and v not in VIEW_ENUM:
            return None  # drop invalid value rather than raise — see note below
        return v

    @field_validator("exposure")
    @classmethod
    def check_exposure(cls, v):
        if v is not None and v not in EXPOSURE_ENUM:
            return None
        return v


class RentTerm(BaseModel):
    rent: Optional[int] = None
    lease_term: Optional[int] = None
    available: Optional[str] = None


class SaleTerm(BaseModel):
    price: Optional[int] = None


class Listing(BaseModel):
    relevant: bool
    reject_reason: Optional[str] = None
    verification_status: str = "unverified"
    for_rent: Optional[bool] = None
    for_sale: Optional[bool] = None
    owner: Owner
    building: Building
    unit: Unit
    features: List[str] = []
    rent_term: RentTerm
    sale_term: SaleTerm

    @field_validator("features")
    @classmethod
    def filter_features(cls, v):
        dropped = [f for f in v if f not in FEATURE_ENUM]
        if dropped:
            print(f"[schema] dropped invalid feature tags: {dropped}")
        return [f for f in v if f in FEATURE_ENUM]
