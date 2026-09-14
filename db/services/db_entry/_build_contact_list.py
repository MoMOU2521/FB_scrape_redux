# db.services.db_entry._build_contact_list.py
from db.db_supabase import get_session, ORG_ID

import logging

logger = logging.getLogger(__name__)


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
