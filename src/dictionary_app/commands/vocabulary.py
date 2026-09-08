"""Interactive vocabulary CRUD commands backed by the Spanglish HTTP API."""

import questionary
from prompt_toolkit import prompt
from rich.console import Console
from rich.table import Table

from src.api_client import SpanglishAPIClient, SpanglishAPIError
from src.api_models import QuizOptions, Vocabulary
from src.utils import normalize_optional_id

console = Console()
PRONOUNS = ("yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas")


def _select_id(message: str, values, default: int | None = None) -> int:
    """Display named API resources and return the selected identifier."""
    choices = [questionary.Choice(item.name, value=item.id) for item in values]
    return questionary.select(message, choices=choices, default=default).ask()


def _collect_translations(target_language_id: int, current=None) -> list[dict]:
    """Collect one or more translations for an API vocabulary payload."""
    translations = []
    existing = [item.translation for item in (current or [])]
    while True:
        default = existing.pop(0) if existing else ""
        text = prompt("Enter a translation: ", default=default).strip()
        if text:
            translations.append({"language_id": target_language_id, "text": text})
        more = prompt("Add another translation [y/N]? ", default="N").strip().lower()
        if more not in ("y", "yes"):
            break
    return translations


def _collect_conjugations(current=None) -> list[dict]:
    """Collect the six present indicative forms used by the original CLI."""
    existing = {item.pronoun: item.form for item in (current or [])}
    conjugations = []
    for pronoun in PRONOUNS:
        form = prompt(
            f"Conjugate for '{pronoun}': ", default=existing.get(pronoun, "")
        ).strip()
        if form:
            conjugations.append(
                {
                    "tense": "present",
                    "mood": "indicative",
                    "pronoun": pronoun,
                    "form": form,
                }
            )
    return conjugations


def _build_payload(options: QuizOptions, current: Vocabulary | None = None) -> dict:
    """Build a create/update payload from interactive API-backed choices."""
    spanish = next(item for item in options.languages if item.code == "es")
    english = next(item for item in options.languages if item.code == "en")
    category_id = _select_id(
        "Select a category",
        options.categories,
        current.categories[0].id if current and current.categories else None,
    )
    vocabulary_type_id = _select_id(
        "Select a vocabulary type",
        options.vocabulary_types,
        current.vocabulary_type.id if current else None,
    )
    chapter_choices = [questionary.Choice("No chapter", value="")] + [
        questionary.Choice(item.name, value=item.id) for item in options.chapters
    ]
    chapter_id = normalize_optional_id(
        questionary.select(
            "Select a chapter (optional)",
            choices=chapter_choices,
            default=current.chapter.id if current and current.chapter else "",
        ).ask()
    )
    text = prompt(
        "Enter the Spanish text: ", default=current.text if current else ""
    ).strip()
    translations = _collect_translations(
        english.id, current.translations if current else None
    )
    category = next(item for item in options.categories if item.id == category_id)
    conjugations = []
    if category.name.casefold() == "verb":
        conjugations = _collect_conjugations(
            current.verb_conjugations if current else None
        )
    return {
        "text": text,
        "language_id": spanish.id,
        "vocabulary_type_id": vocabulary_type_id,
        "chapter_id": chapter_id,
        "category_ids": [category_id],
        "translations": translations,
        "conjugations": conjugations,
    }


def add_vocabulary(client: SpanglishAPIClient | None = None) -> None:
    """Create one or more vocabulary cards through the API."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        options = client.get_quiz_options()
        while True:
            created = client.create_vocabulary(_build_payload(options))
            translations = ", ".join(item.translation for item in created.translations)
            console.print(f"[green]Added:[/] {created.text} -> {translations}")
            more = prompt("Add another text [y/N]? ", default="N").strip().lower()
            if more not in ("y", "yes"):
                break
    except (SpanglishAPIError, StopIteration) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def list_vocabulary(client: SpanglishAPIClient | None = None) -> None:
    """List API vocabulary with optional category and page-size filters."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        options = client.get_quiz_options()
        choices = [questionary.Choice("All", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.categories
        ]
        category_id = normalize_optional_id(
            questionary.select("Select a category", choices=choices).ask()
        )
        chapter_choices = [questionary.Choice("All chapters", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.chapters
        ]
        chapter_id = normalize_optional_id(
            questionary.select("Select a chapter", choices=chapter_choices).ask()
        )
        page_size = int(prompt("How many records? ", default="10"))
        randomize = questionary.confirm("Randomize selection?", default=False).ask()
        page = client.list_vocabulary(
            page_size=page_size,
            category_id=category_id,
            chapter_id=chapter_id,
            randomize=randomize,
        )
        _print_vocabulary(page.items)
    except (SpanglishAPIError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def update_vocabulary(client: SpanglishAPIClient | None = None) -> None:
    """Replace a vocabulary card selected by its API identifier."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        vocabulary_id = int(prompt("Vocabulary ID to update: "))
        current = client.get_vocabulary(vocabulary_id)
        updated = client.update_vocabulary(
            vocabulary_id, _build_payload(client.get_quiz_options(), current)
        )
        console.print(f"[green]Updated:[/] {updated.text}")
    except (SpanglishAPIError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def delete_vocabulary(client: SpanglishAPIClient | None = None) -> None:
    """Delete a vocabulary card after explicit terminal confirmation."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        vocabulary_id = int(prompt("Vocabulary ID to delete: "))
        vocabulary = client.get_vocabulary(vocabulary_id)
        confirmed = questionary.confirm(
            f"Delete '{vocabulary.text}'?", default=False
        ).ask()
        if confirmed:
            client.delete_vocabulary(vocabulary_id)
            console.print(f"[green]Deleted:[/] {vocabulary.text}")
    except (SpanglishAPIError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def create_chapter(client: SpanglishAPIClient | None = None) -> None:
    """Create a chapter that can optionally group vocabulary and quizzes."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        name = prompt("Chapter name: ").strip()
        if not name:
            raise ValueError("Chapter name cannot be empty")
        chapter = client.create_chapter(name)
        console.print(f"[green]Created chapter:[/] {chapter.name} (ID {chapter.id})")
    except (SpanglishAPIError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def _print_vocabulary(items: list[Vocabulary]) -> None:
    """Render vocabulary cards in a compact terminal table."""
    table = Table(title="Vocabulary", show_lines=True)
    for heading in (
        "ID",
        "Text",
        "Chapter",
        "Categories",
        "Translations",
        "Conjugations",
    ):
        table.add_column(heading)
    for item in items:
        table.add_row(
            str(item.id),
            item.text,
            item.chapter.name if item.chapter else "—",
            ", ".join(category.name for category in item.categories),
            ", ".join(value.translation for value in item.translations),
            ", ".join(
                f"{value.pronoun}: {value.form}" for value in item.verb_conjugations
            ),
        )
    console.print(table)


# Preserve the original command import while exposing the clearer function name.
list = list_vocabulary
