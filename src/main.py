import typer
import questionary
from rich.console import Console
from rich.table import Table

from .db import crud
from .enums import CategoryEnum

app = typer.Typer()
console = Console()

@app.command()
def add_word(interactive: bool = True):
    while interactive:
        word = typer.prompt("Enter the Spanish word").capitalize()
        # Typer automatically provides choices for Enum
        # category: CategoryEnum = typer.prompt(
        #     "Choose category",
        #     show_choices=True
        # )
        category = questionary.select("Select a category", choices=CategoryEnum).ask()
        translation = typer.prompt("Enter the translation").capitalize()

        w = crud.create_word(word, category, translation)
        console.print(f"[green]Added:[/] {w.word} ({w.category}) → {w.translation}")

        more = typer.confirm("Add another word?", default=True)
        if not more:
            break

@app.command()
def add_verb(word_id: int, yo: str, tu: str, ella_el: str,
             nosotros: str, vosotros: str, ellos_ellas: str):
    crud.create_verb(word_id, yo, tu, ella_el, nosotros, vosotros, ellos_ellas)
    console.print("[green]Verb added.[/green]")

@app.command()
def list_words(category: CategoryEnum = typer.Option(None)):
    rows = crud.list_words(category)

    table = Table(title="Words", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Word")
    table.add_column("Category")
    table.add_column("Translation")

    for w in rows:
        table.add_row(str(w.id), w.word, w.category, w.translation)

    console.print(table)

@app.command()
def list_verbs():
    rows = crud.list_verbs()

    table = Table(title="Verbs", show_lines=True)
    table.add_column("Verb")
    table.add_column("yo")
    table.add_column("tu")
    table.add_column("ella/el")
    table.add_column("nosotros")
    table.add_column("vosotros")
    table.add_column("ellos_ellas")

    for v in rows:
        table.add_row(
            v.word.word,
            v.yo, v.tu, v.ella_el, v.nosotros, v.vosotros, v.ellos_ellas
        )

    console.print(table)

if __name__ == "__main__":
    app()
