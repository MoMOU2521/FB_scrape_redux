# db.helpers.py
import re

ANONYMOUS_AUTHORS = {"anonymous", "anonymous member"}


def is_anonymous_author(author) -> bool:
    return not author or author.strip().lower() in ANONYMOUS_AUTHORS

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


def normalize_author(author):
    """Normalize all apostrophe variations to standard ASCII apostrophe."""
    if not author:
        return author
    return (
        author.replace("’", "'").replace("ʼ", "'").replace("‘", "'").replace("‛", "'")
    )
