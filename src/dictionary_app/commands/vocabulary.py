"""Interactive vocabulary CRUD commands backed by the Spanglish HTTP API."""

from dataclasses import dataclass

import questionary
from prompt_toolkit import prompt
from rich.console import Console
from rich.table import Table

from src.api_client import SpanglishAPIClient, SpanglishAPIError
from src.api_models import QuizOptions, Vocabulary
from src.utils import confirm_with_quit, normalize_optional_id, select_with_quit

console = Console()
PRONOUNS = ("yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas")


@dataclass(frozen=True)
class VocabularyContext:
    """Selections shared by every vocabulary item in one entry batch."""

    category_id: int
    chapter_id: int | None
    song_id: int | None = None


def _select_song(client: SpanglishAPIClient, current: Vocabulary | None = None) -> int:
    """Choose or create an artist and then choose or create one of their songs."""
    artists = client.list_artists()
    artist_choices = [questionary.Choice(item.name, value=item.id) for item in artists]
    artist_choices.append(questionary.Choice("+ Add artist", value="new"))
    artist_id = select_with_quit(
        "Select an artist",
        artist_choices,
        default=current.song.artist.id if current and current.song else None,
    )
    if artist_id == "new":
        name = prompt("Artist name: ").strip()
        if not name:
            raise ValueError("Artist name cannot be empty")
        artist_id = client.create_artist(name).id
    songs = client.list_songs(artist_id)
    song_choices = [questionary.Choice(item.title, value=item.id) for item in songs]
    song_choices.append(questionary.Choice("+ Add song", value="new"))
    song_id = select_with_quit(
        "Select a song",
        song_choices,
        default=current.song.id if current and current.song else None,
    )
    if song_id == "new":
        title = prompt("Song title: ").strip()
        if not title:
            raise ValueError("Song title cannot be empty")
        song_id = client.create_song(title, artist_id).id
    return song_id


def _select_id(message: str, values, default: int | None = None) -> int:
    """Display named API resources and return the selected identifier."""
    choices = [questionary.Choice(item.name, value=item.id) for item in values]
    return select_with_quit(message, choices, default=default)


def _collect_translations(target_language_id: int, current=None) -> list[dict]:
    """Collect one or more translations for an API vocabulary payload."""
    translations = []
    existing = [item.translation for item in (current or [])]
    while True:
        default = existing.pop(0) if existing else ""
        text = prompt("Enter a translation: ", default=default).strip()
        if text:
            translations.append({"language_id": target_language_id, "text": text})
        if not confirm_with_quit("Add another translation?", default=False):
            break
    return translations


def _collect_conjugations(current=None) -> list[dict]:
    """Collect the six present indicative forms used by the original CLI."""
    existing = {item.pronoun: item.form for item in (current or [])}
    conjugations: list[dict] = []
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


def _select_vocabulary_context(
    options: QuizOptions,
    current: Vocabulary | None = None,
    client: SpanglishAPIClient | None = None,
) -> VocabularyContext:
    """Collect category and optional chapter selections."""
    category_id = _select_id(
        "Select a category",
        options.categories,
        current.categories[0].id if current and current.categories else None,
    )
    category = next(item for item in options.categories if item.id == category_id)
    if category.name.casefold() in {"song", "songs"} and client:
        return VocabularyContext(category_id, None, _select_song(client, current))
    chapter_choices = [questionary.Choice("No chapter", value="")] + [
        questionary.Choice(item.name, value=item.id) for item in options.chapters
    ]
    chapter_id = normalize_optional_id(
        select_with_quit(
            "Select a chapter (optional)",
            chapter_choices,
            default=current.chapter.id if current and current.chapter else "",
        )
    )
    return VocabularyContext(category_id, chapter_id)


def _build_payload(
    options: QuizOptions,
    current: Vocabulary | None = None,
    context: VocabularyContext | None = None,
    client: SpanglishAPIClient | None = None,
) -> dict:
    """Build a create/update payload from interactive API-backed choices."""
    spanish = next(item for item in options.languages if item.code == "es")
    english = next(item for item in options.languages if item.code == "en")
    context = context or _select_vocabulary_context(options, current, client)
    text = prompt(
        "Enter the Spanish text: ", default=current.text if current else ""
    ).strip()
    translations = _collect_translations(
        english.id, current.translations if current else None
    )
    category = next(
        item for item in options.categories if item.id == context.category_id
    )
    conjugations = []
    if category.name.casefold() == "verb":
        conjugations = _collect_conjugations(
            current.verb_conjugations if current else None
        )
    return {
        "text": text,
        "language_id": spanish.id,
        "chapter_id": context.chapter_id,
        "song_id": context.song_id,
        "category_ids": [context.category_id],
        "translations": translations,
        "conjugations": conjugations,
    }


def add_vocabulary(client: SpanglishAPIClient | None = None) -> None:
    """Create one or more vocabulary cards through the API."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        options = client.get_quiz_options()
        context = _select_vocabulary_context(options, client=client)
        while True:
            created = client.create_vocabulary(_build_payload(options, context=context))
            translations = ", ".join(item.translation for item in created.translations)
            console.print(f"[green]Added:[/] {created.text} -> {translations}")
            if not confirm_with_quit("Add another text?", default=False):
                break
    except (SpanglishAPIError, StopIteration, ValueError) as exc:
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
            select_with_quit("Select a category", choices)
        )
        chapter_choices = [questionary.Choice("All chapters", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.chapters
        ]
        chapter_id = normalize_optional_id(
            select_with_quit("Select a chapter", chapter_choices)
        )
        page_size = int(prompt("How many records? ", default="10"))
        randomize = confirm_with_quit("Randomize selection?", default=False)
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
            vocabulary_id,
            _build_payload(client.get_quiz_options(), current, client=client),
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
        confirmed = confirm_with_quit(f"Delete '{vocabulary.text}'?", default=False)
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


def create_category(client: SpanglishAPIClient | None = None) -> None:
    """Create a category used to organize vocabulary and quizzes."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        name = prompt("Category name: ").strip()
        if not name:
            raise ValueError("Category name cannot be empty")
        category = client.create_category(name)
        console.print(f"[green]Created category:[/] {category.name} (ID {category.id})")
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
        "Song",
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
            f"{item.song.title} — {item.song.artist.name}" if item.song else "—",
            ", ".join(category.name for category in item.categories),
            ", ".join(value.translation for value in item.translations),
            ", ".join(
                f"{value.pronoun}: {value.form}" for value in item.verb_conjugations
            ),
        )
    console.print(table)
