# db.services.db_entry.resolve_or_create_owner.py
from sqlalchemy import insert

from pydantic import ValidationError

from db.db_supabase import ORG_ID
from db.db_tables import (
    owner_registry,
    owner_contact,
)
from db.db_schemas import (
    OwnerContactCreate,
)
from db.services.db_entry._build_contact_list import _build_contact_list
from db.services.db_entry._resolve_owner_name import _resolve_owner_name
from db.services.db_entry._search_owners_duplicate import _search_owners_duplicate
from db.services.db_entry._get_owner_contacts import _get_owner_contacts
from db.helpers import normalize_phone_th
from db.exceptions import OwnerConflictError, NoIdentifiableOwnerError

import logging

logger = logging.getLogger(__name__)


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
            # print(
            #     f"insert owner_contacts:\n  owner_id: {owner_id}\n  count: {len(new_contacts)}"
            # )

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

    # print(f"insert owner:\n  id: {owner_id}\n  name: {name}")

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
        # print(
        #     f"insert owner_contacts:\n  owner_id: {owner_id}\n  count: {len(validated_contacts)}"
        # )

    return owner_id
