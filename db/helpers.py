# db.helpers.py
import re


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


def normalize_author(author):
    """Normalize all apostrophe variations to standard ASCII apostrophe."""
    if not author:
        return author
    return (
        author.replace("’", "'").replace("ʼ", "'").replace("‘", "'").replace("‛", "'")
    )
