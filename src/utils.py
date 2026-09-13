"""Add general utility functions here that can be used across the project."""

from typing import Any

import questionary

BOOLEAN_CHOICES = {"y": True, "n": False, "yes": True, "no": False}
QUIT_VALUE = object()


class QuitRequested(Exception):
    """Signal that the user selected the global Quit menu entry."""


def quit_choice() -> questionary.Choice:
    """Return the visually distinct Quit entry shared by selection menus."""
    return questionary.Choice(
        [("fg:#ff0000 bold", "Quit")], value=QUIT_VALUE, shortcut_key="q"
    )


def select_with_quit(
    message: str,
    choices: list[Any],
    *,
    default: Any = None,
) -> Any:
    """Display a selection with a red Quit entry and raise when selected."""
    selected = questionary.select(
        message,
        choices=[*choices, quit_choice()],
        default=default,
    ).ask()
    if selected is QUIT_VALUE:
        raise QuitRequested
    return selected


def confirm_with_quit(message: str, *, default: bool = False) -> bool:
    """Ask a yes/no question using selectable choices plus the red Quit entry."""
    choices = [
        questionary.Choice("Yes", value=True),
        questionary.Choice("No", value=False),
    ]
    return select_with_quit(message, choices, default=default)


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
