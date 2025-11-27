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
        category = questionary.select("Select a category", choices=CategoryEnum).ask()

        translations = []
        while True:
            t = typer.prompt("Enter a translation").strip().lower()
            translations.append(t)

            more = typer.confirm("Add another translation?", default=False)
            if not more:
                break
        
        w = crud.create_word(word, category, translations=translations)
        translation = ",".join(t for t in translations)
        console.print(f"[green]Added:[/] {w.word} ({w.category}) -> {translation}")

        if category == CategoryEnum.VERB:
            word_id = w.id
            yo = typer.prompt("Enter the verb for yo").strip().capitalize()
            tu = typer.prompt("Enter the verb for tu").strip().capitalize()
            ella_el = typer.prompt("Enter the verb for ella_el").strip().capitalize()
            nosotros = typer.prompt("Enter the verb for nosotros").strip().capitalize()
            vosotros = typer.prompt("Enter the verb for vosotros").strip().capitalize()
            ellos_ellas = typer.prompt("Enter the verb for ellos_ellas").strip().capitalize()

            add_verb(
                word_id=word_id, 
                yo=yo, 
                tu=tu, 
                ella_el=ella_el,
                nosotros=nosotros,
                vosotros=vosotros,
                ellos_ellas=ellos_ellas
            )

        more = typer.confirm("Add another word?", default=True)
        if not more:
            break


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
    table.add_column("Translations")

    for w in rows:
        table.add_row(str(w.id), w.word, w.category, ",".join(t.translation for t in w.translations))

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
