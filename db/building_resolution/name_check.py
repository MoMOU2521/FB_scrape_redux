# db/building_resolution/name_check.py
import re

_THAI_RE = re.compile(r"[\u0E00-\u0E7F]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def has_usable_latin_name(name: str | None) -> bool:
    """True if name is present and contains no Thai script.
    Doesn't require pure-Latin — allows numbers/punctuation —
    just rejects Thai characters as disqualifying."""
    if not name or not name.strip():
        return False
    if _THAI_RE.search(name):
        return False
    if not _LATIN_RE.search(name):
        return False  # no Thai, but also no Latin letters — e.g. pure symbols/numbers
    return True


def get_best_available_name(building: dict) -> tuple[str | None, bool]:
    """
    Returns (name, needs_ai_transliteration)
    Checks standardized first, then raw, in that order.
    """
    standardized = building.get("building_name_standardized")
    raw = building.get("building_name")

    if has_usable_latin_name(standardized):
        return standardized, False

    if has_usable_latin_name(raw):
        return raw, False

    # neither usable — need AI transliteration
    # prefer standardized as source hint if present, else raw
    return (standardized or raw), True
