# db.services.db_entry._resolve_owner_name.py
import logging

logger = logging.getLogger(__name__)


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
