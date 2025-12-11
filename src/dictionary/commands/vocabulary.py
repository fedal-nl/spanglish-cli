import questionary
import typer
from prompt_toolkit.shortcuts import choice
from rich.console import Console
from rich.table import Table

from src.db import crud
from src.enums import CategoryEnum

app = typer.Typer(
    add_completion=False,
    help="📝 Dictionary management commands: add, list words, sentences and verbs."
)
console = Console()


@app.command()
def add(interactive: bool = True):
    """Add a new text to the database along with its translations.
    If the word is a verb, also add its conjugations.
    """
    while interactive:

        category = questionary.select(
            "Select a category",
            choices=CategoryEnum
        ).ask()
        text = typer.prompt("Enter the Spanish text").capitalize()
        translations = []
        while True:
            t = typer.prompt("Enter a translation").strip().lower()
            translations.append(t)

            more = typer.confirm("Add another translation?", default=False)
            if not more:
                break

        added_text = crud.add_text_to_dictionary(
            text=text,
            category=category,
            translations=translations
        )
        translation = ",".join(t for t in translations)
        console.print(f"[green]Added:[/] {added_text.text} ({added_text.category}) -> \
                      {translation}")

        if category == CategoryEnum.VERB:
            text_id = added_text.id
            yo = typer.prompt("Enter the verb for yo").strip().capitalize()
            tu = typer.prompt("Enter the verb for tu").strip().capitalize()
            ella_el = typer.prompt("Enter the verb for ella_el").strip().capitalize()
            nosotros = typer.prompt("Enter the verb for nosotros").strip().capitalize()
            vosotros = typer.prompt("Enter the verb for vosotros").strip().capitalize()
            ellos_ellas = typer.prompt("Enter the verb for ellos_ellas").strip().capitalize()

            add_verb(
                text_id=text_id,
                yo=yo,
                tu=tu,
                ella_el=ella_el,
                nosotros=nosotros,
                vosotros=vosotros,
                ellos_ellas=ellos_ellas
            )

        more = typer.confirm("Add another text?", default=True)
        if not more:
            break


def add_verb(text_id: int, yo: str, tu: str, ella_el: str,
             nosotros: str, vosotros: str, ellos_ellas: str):
    crud.create_verb(text_id, yo, tu, ella_el, nosotros, vosotros, ellos_ellas)
    console.print("[green]Verb added.[/green]")

@app.command()
def list():
    """List all texts in the database. Optionally filter by category,
    limit the number of records, and randomize the selection.
    """
    category = choice(
        message="Select a category ?",
        options=[(None, "All")] + [(c, c.name) for c in CategoryEnum],
        default="All"
    )

    limit = typer.prompt("How many records ?", default=10, type=int)
    is_random = typer.confirm("Random words ?", default=False)

    raws = crud.list_dictionary_entries(
        category=category,
        limit=limit,
        is_random=is_random
    )

    table = Table(title="Texts", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Text")
    table.add_column("Category")
    table.add_column("Translations")
    table.add_column("Verb", style="magenta")
    table.add_column("yo", style="magenta")
    table.add_column("tu", style="magenta")
    table.add_column("ella/el", style="magenta")
    table.add_column("nosotros", style="magenta")
    table.add_column("vosotros", style="magenta")
    table.add_column("ellos_ellas", style="magenta")

    for data in raws:
        table.add_row(
            str(data.id),
            data.text,
            data.category,
            ",".join(t.translation for t in data.translations),
            "Is verb" if data.verb else "",
            data.verb.yo if data.verb else "",
            data.verb.tu if data.verb else "",
            data.verb.ella_el if data.verb else "",
            data.verb.nosotros if data.verb else "",
            data.verb.vosotros if data.verb else "",
            data.verb.ellos_ellas if data.verb else ""
        )

    console.print(table)

@app.command()
def list_verbs():
    """List all verbs in the database along with their conjugations."""
    raws = crud.list_verbs()

    table = Table(title="Verbs", show_lines=True)
    table.add_column("Verb")
    table.add_column("yo")
    table.add_column("tu")
    table.add_column("ella/el")
    table.add_column("nosotros")
    table.add_column("vosotros")
    table.add_column("ellos_ellas")

    for v in raws:
        table.add_row(
            v.dictionary.text,
            v.yo, v.tu, v.ella_el, v.nosotros, v.vosotros, v.ellos_ellas
        )

    console.print(table)
