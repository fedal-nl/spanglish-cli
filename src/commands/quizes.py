import questionary
import typer
from rich.console import Console
from rich.progress import Progress

from src.db import crud
from src.enums import CategoryEnum
from src.progressbars.quiz import quiz_progress

app = typer.Typer()
console = Console()

@app.command()
def start_quiz():
    """Start a quiz session..."""

    quiz_session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID:[/] {quiz_session.id}")

    # ---------- INITIAL USER PROMPTS ----------
    with_category = typer.confirm(
        "Do you want to filter by Category ?", default=False
    )

    category = None
    if with_category:
        category = questionary.select(
            "Select a category", 
            choices=CategoryEnum
        ).ask()

    limit = typer.prompt("How many records ?", default=10, type=int)

    rows = crud.list_words(category=category, limit=limit, is_random=True)
    # ------------------------------------------

    correct_answers = 0
    incorrect_answers = 0

    # ---------- PROGRESS BAR ----------
    with Progress(*quiz_progress, console=console) as progress:

        task = progress.add_task("Quiz Progress", total=len(rows))

        for i, w in enumerate(rows, 1):

            # Advance progress bar
            progress.update(task, advance=1)

            progress.update(
                task,
                description=f"Question {i} of {len(rows)}"
            )

            # ===============================
            #     >>> PAUSE PROGRESS <<<
            # ===============================
            progress.stop()

            # ----- ASK THE QUESTION -----
            console.print(f"\n[bold blue]Word:[/] {w.word} ({w.category})")

            user_translation = typer.prompt("Enter the translation").strip().lower()
            answered_correctly = False

            correct_translations = [
                t.translation.lower() for t in w.translations
            ]

            if user_translation in correct_translations:
                answered_correctly = True

                # Verb conjugation section
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

            # ===============================
            #    >>> RESUME PROGRESS <<<
            # ===============================
            progress.start()

            # ----- SAVE ATTEMPT -----
            crud.create_quiz_attempt(
                session_id=quiz_session.id,
                word_id=w.id,
                answered_correctly=answered_correctly
            )

            if answered_correctly:
                console.print("[green]Correct![/green]")
                correct_answers += 1
            else:
                console.print("[red]Incorrect![/red]")
                incorrect_answers += 1

    console.print("\n[bold green]Quiz session ended.[/bold green]")
    console.print(f"Correct answers: {correct_answers} out of {len(rows)}")
    console.print(f"Incorrect answers: {incorrect_answers} out of {len(rows)}")
