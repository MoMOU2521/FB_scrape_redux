# db.services.db_entry._resolve_owner_name.py
import logging
from db.helpers import is_anonymous_author

logger = logging.getLogger(__name__)


def _resolve_owner_name(author: str, contacts: list[dict]):
    if not is_anonymous_author(author):
        return author
    if contacts:
        first = contacts[0]
        if first.get("contact_name"):
            return first["contact_name"]
        if first.get("contact_value"):
            return first["contact_value"]
    return None
