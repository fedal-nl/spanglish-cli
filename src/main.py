import questionary
import typer
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
def list_words():
    """List all words in the database. Optionally filter by category, 
    limit the number of records, and randomize the selection.
    """
    category: bool = None
    limit: int|None = None
    is_random: bool = False

    # check with the user
    with_category = typer.confirm(
        "Do you want to filer by Category ?", default=False
    )

    if with_category:
        category = questionary.select("Select a category", choices=CategoryEnum).ask()

    limit = typer.prompt("How many records ?", default=10, type=int)
    is_random = typer.confirm("Random words ?", default=False)

    rows = crud.list_words(category=category, limit=limit, is_random=is_random)

    table = Table(title="Words", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Word")
    table.add_column("Category")
    table.add_column("Translations")
    table.add_column("Verb", style="magenta")
    table.add_column("yo", style="magenta")
    table.add_column("tu", style="magenta")
    table.add_column("ella/el", style="magenta")
    table.add_column("nosotros", style="magenta")
    table.add_column("vosotros", style="magenta")
    table.add_column("ellos_ellas", style="magenta")

    for w in rows:
        table.add_row(
            str(w.id),
            w.word,
            w.category,
            ",".join(t.translation for t in w.translations),
            "Is verb" if w.verb else "",
            w.verb.yo if w.verb else "",
            w.verb.tu if w.verb else "",
            w.verb.ella_el if w.verb else "",
            w.verb.nosotros if w.verb else "",
            w.verb.vosotros if w.verb else "",
            w.verb.ellos_ellas if w.verb else ""
        )

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


@app.command()
def start_quiz():
    """Start a quiz session. It will call the list words function to get all the words
    needed for the quiz then it will prompt the user with questions. It starts with
    saving the quiz session in the database and then for each word it will create
    a quiz attempt record in the database as well. For any correct answer, the
    answered_correctly field will be set to True otherwise False.
    """
    quiz_session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID:[/] {quiz_session.id}")

    category: bool = None
    limit: int|None = None
    is_random: bool = True

    # check with the user
    with_category = typer.confirm(
        "Do you want to filer by Category ?", default=False
    )

    if with_category:
        category = questionary.select("Select a category", choices=CategoryEnum).ask()

    limit = typer.prompt("How many records ?", default=10, type=int)

    rows = crud.list_words(category=category, limit=limit, is_random=is_random)

    correct_answers = 0

    # First ask for the translation. If it is correct, then mark the answered_correctly
    # as True answer. If it is a Verb also then also ask for the verb conjugations.
    # if any of the answers is wrong, then mark the answered_correctly as False and
    # move to the next word.
    for w in rows:
        console.print(f"\n[bold blue]Word:[/] {w.word} ({w.category})")
        user_translation = typer.prompt("Enter the translation").strip().lower()

        answered_correctly = False

        correct_translations = [t.translation.lower() for t in w.translations]
        if user_translation in correct_translations:
            answered_correctly = True

            if w.category == CategoryEnum.VERB:
                console.print("[bold blue]Now conjugate the verb:[/bold blue]")
                user_yo = typer.prompt("yo").strip().capitalize()
                user_tu = typer.prompt("tu").strip().capitalize()
                user_ella_el = typer.prompt("ella/el").strip().capitalize()
                user_nosotros = typer.prompt("nosotros").strip().capitalize()
                user_vosotros = typer.prompt("vosotros").strip().capitalize()
                user_ellos_ellas = typer.prompt("ellos_ellas").strip().capitalize()

                verb = w.verb
                if not (
                    user_yo == verb.yo and
                    user_tu == verb.tu and
                    user_ella_el == verb.ella_el and
                    user_nosotros == verb.nosotros and
                    user_vosotros == verb.vosotros and
                    user_ellos_ellas == verb.ellos_ellas
                ):
                    answered_correctly = False

        crud.create_quiz_attempt(
            session_id=quiz_session.id,
            word_id=w.id,
            answered_correctly=answered_correctly
        )

    console.print("\n[bold green]Quiz session ended.[/bold green]")
    console.print(f"Correct answers: {correct_answers} out of {len(rows)}")


if __name__ == "__main__":
    app()
