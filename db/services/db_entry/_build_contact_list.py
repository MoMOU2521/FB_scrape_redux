# db.services.db_entry._build_contact_list.py
from db.db_supabase import get_session, ORG_ID
from db.helpers import is_anonymous_author

import logging

logger = logging.getLogger(__name__)


def _build_contact_list(gate1_contacts: list[dict], author: str) -> list[dict]:
    contacts = list(gate1_contacts)
    if not is_anonymous_author(author):
        contacts.append(
            {
                "contact_name": None,
                "contact_type": "facebook",
                "contact_value": author,
                "contact_note": None,
            }
        )
    return contacts
