"""Add general utility functions here that can be used across the project."""

BOOLEAN_CHOICES = {"y": True, "n": False, "yes": True, "no": False}


def normalize_optional_id(value: int | str | None) -> int | None:
    """Normalize an optional menu identifier without sending labels to the API."""
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized or normalized.casefold() in {"all", "none"}:
            return None
        return int(normalized)
    return value


def optional_id_list(value: int | str | None) -> list[int]:
    """Return an API list filter containing zero or one normalized identifier."""
    normalized = normalize_optional_id(value)
    return [] if normalized is None else [normalized]
