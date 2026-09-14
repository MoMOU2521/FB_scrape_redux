# db.exceptions.py
class OwnerConflictError(Exception):
    """2+ existing owners match this post's contacts."""

    pass


class NoIdentifiableOwnerError(Exception):
    """Author unusable and no contact provides a name."""

    pass


class BuildingConflictError(Exception):
    """2+ existing buildings match this post's building name."""

    pass


class BuildingNotFoundError(Exception):
    """No exact building match found — building lookup/creation is out of
    scope for this pipeline, so this post cannot proceed."""

    pass
