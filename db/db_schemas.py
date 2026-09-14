# db.db_schemas.py
#
# Pydantic validation shapes, copied (not imported) from the main app.
# Used to validate gate1 JSON before building Core insert() values.

import re
from datetime import date
from typing import Optional
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    TypeAdapter,
    EmailStr,
    ValidationError,
)

PHONE_REGEX = re.compile(r"^\+?\d{9,15}$")
_email_adapter = TypeAdapter(EmailStr)


# CONFIRM exact values against the real app.types.enums.ContactType
class ContactType(str, Enum):
    email = "email"
    phone = "phone"
    facebook = "facebook"
    line_id = "line_id"
    whatsapp = "whatsapp"
    other = "other"


class OwnerContactCreate(BaseModel):
    contact_name: Optional[str] = Field(None, max_length=100)
    contact_type: ContactType
    contact_value: str = Field(min_length=1, max_length=100)
    contact_note: Optional[str] = Field(None, max_length=50)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("contact_value", mode="before")
    def _validate_contact_value(cls, v: str, info):
        ct = info.data.get("contact_type")
        if ct == ContactType.phone:
            if not PHONE_REGEX.match(v):
                raise ValueError("Enter a valid phone number (+9-15 digits).")
        elif ct == ContactType.email:
            try:
                _email_adapter.validate_python(v)
            except ValidationError:
                raise ValueError("Enter a valid email address.")
        return v


class OwnerRegistryCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    contacts: list[OwnerContactCreate]
    # Deliberately Optional, unlike the main app's required field.
    # owner_note table is out of scope for this pipeline — always None.
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VerificationStatus(str, Enum):
    unverified = "unverified"
    open = "open"
    # CONFIRM remaining values against app.types.enums.VerificationStatus


class PropertyRegistryCreate(BaseModel):
    # NOTE: for_sale/for_rent are bool (not Optional) here, matching the
    # main app's schema exactly. Gate1 can produce null for these — how
    # null should be handled is an OPEN QUESTION, not decided. See db_entry.py.
    for_sale: bool
    for_rent: bool
    verification_status: VerificationStatus
    # fb_posted deliberately NOT included — not in gate1 JSON, not told
    # a value to set, so this pipeline never sets it at all.

    model_config = ConfigDict(from_attributes=True)


class ExposureType(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"
    northeast = "northeast"
    northwest = "northwest"
    southeast = "southeast"
    southwest = "southwest"


class ViewType(str, Enum):
    city = "city"
    river = "river"
    park = "park"
    garden = "garden"
    pool = "pool"


class FeatureType(str, Enum):
    pet_allowed = "pet_allowed"
    unfurnished = "unfurnished"
    washer = "washer"
    dryer = "dryer"
    oven = "oven"
    bathtub = "bathtub"
    open_bedroom = "open_bedroom"
    loft_bed = "loft_bed"
    walk_in_closet = "walk_in_closet"
    closed_kitchen = "closed_kitchen"
    extra_kitchen = "extra_kitchen"
    maidroom = "maidroom"
    multi_use_room = "multi_use_room"
    corner_unit = "corner_unit"
    duplex = "duplex"
    terrace = "terrace"
    penthouse = "penthouse"
    pool_villa = "pool_villa"


class PropertyFeatureCreate(BaseModel):
    feature: FeatureType

    model_config = ConfigDict(from_attributes=True)


class CAUnitCreate(BaseModel):
    building_id: int
    room_number: Optional[str] = Field(None, max_length=25)
    floor: Optional[str] = Field(None, max_length=10)
    tower: Optional[str] = Field(None, max_length=10)
    bedroom: Optional[int] = Field(None, ge=0, le=10)
    bathroom: Optional[int] = Field(None, ge=1, le=10)
    sqm: Optional[float] = Field(None, ge=0, le=99999.99)
    exposure: Optional[ExposureType] = None
    view: Optional[ViewType] = None

    model_config = ConfigDict(from_attributes=True)


class RentTermCreate(BaseModel):
    rent: int = Field(ge=0, le=999999)
    lease_term: Optional[int] = Field(None, ge=3, le=36)
    available: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class SaleTermCreate(BaseModel):
    price: int = Field(ge=0, le=999999999)
    # sale_term_type never produced by gate1 — always None, never set.

    model_config = ConfigDict(from_attributes=True)


# class VerificationStatus(str, Enum):
#     unverified = "unverified"
#     open = "open"
#     verified = "verified"


# class PropertyRegistryCreate(BaseModel):
#     for_sale: bool = False
#     for_rent: bool = False
#     verification_status: VerificationStatus
#     # fb_posted intentionally excluded — always left null, never set here.

#     model_config = ConfigDict(from_attributes=True)
