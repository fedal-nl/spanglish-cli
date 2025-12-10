import typer
from prompt_toolkit.shortcuts import choice
from rich.console import Console
from rich.progress import Progress

from src.db import crud
from src.dictionary.commands.quiz.factory import convert_dictionary_to_quiz_item
from src.enums import CategoryEnum, LanguageEnum
from src.progressbars.quiz import quiz_progress
from src.dictionary.commands.quiz.scores import get_score

app = typer.Typer(
    add_completion=False,
    help="🎯 Quiz commands: start quizzes and view performance."
)
console = Console()

@app.command()
def start():
    """Start a quiz session..."""

    # ---------- INITIAL USER PROMPTS ----------
    category = choice(
        message="Select a category ?",
        options=[(None, "All")] + [(c, c.name) for c in CategoryEnum],
        default="All"
    )

    language = choice(
        message="Select a language ?",
        options=[(c, c.name) for c in LanguageEnum],
        default=LanguageEnum.ENGLISH
    )

    limit = typer.prompt("How many records ?", default=10, type=int)
    is_random = typer.confirm("Randomize selection ?", default=True)

    quiz_session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID:[/] {quiz_session.id}")

    # ---------- LOAD QUIZ ITEMS ----------
    rows = crud.list_dictionary_entries(
        category=category,
        limit=limit,
        is_random=is_random
    )
    # Convert to quiz items
    quiz_items = [convert_dictionary_to_quiz_item(w, language) for w in rows]

    correct_answers = 0
    incorrect_answers = 0

    # ---------- PROGRESS BAR ----------
    with Progress(*quiz_progress, console=console) as progress:

        task = progress.add_task("Quiz Progress", total=len(quiz_items))

        for index, item in enumerate(quiz_items, 1):

            # Advance progress bar
            progress.update(task, advance=1)

            progress.update(
                task,
                description=f"Question {index} of {len(quiz_items)}"
            )

            # ===============================
            #     >>> PAUSE PROGRESS <<<
            # ===============================
            progress.stop()
            answered_correctly = True
            question_started = True
            answer = ""
            while answered_correctly and question_started:
                console.print("[yellow]Take your time to think...[/yellow]")
                # If the selected language is English, the question will be shown in
                # English
                # ----- SHOW HINT IF Spanish -----
                if language == LanguageEnum.ENGLISH:
                    question = item.question
                    console.print(f"\n[bold blue]Translate to Spanish:[/] {question}")

                    answer = typer.prompt("Enter the translation").strip().lower()
                    answered_correctly = get_score(answer, item.answer)
                else:
                    # ----- ASK THE QUESTION -----
                    console.print(
                        f"\n[bold blue]Word:[/] {item.question} ({item.category})"
                    )
                    answer = typer.prompt("Enter the translation").strip().lower()
                    answered_correctly = get_score(answer, item.answer)
                # ----- SHOW VERB CONJUGATIONS -----
                # TODO: Refactor this into a separate function
                if item.conjugation:
                    console.print("[bold blue]Now conjugate the verb:[/bold blue]")

                    user_yo = typer.prompt("yo").strip().capitalize()
                    answered_correctly = get_score(user_yo, item.conjugation["yo"])

                    user_tu = typer.prompt("tu").strip().capitalize()
                    answered_correctly = get_score(user_tu, item.conjugation["tú"])

                    user_ella_el = typer.prompt("ella/el").strip().capitalize()
                    answered_correctly = get_score(
                        user_ella_el, item.conjugation["él/ella"]
                    )

                    user_nosotros = typer.prompt("nosotros").strip().capitalize()
                    answered_correctly = get_score(
                        user_nosotros, item.conjugation["nosotros"]
                    )

                    user_vosotros = typer.prompt("vosotros").strip().capitalize()
                    answered_correctly = get_score(
                        user_vosotros, item.conjugation["vosotros"]
                    )

                    user_ellos_ellas = typer.prompt("ellos_ellas").strip().capitalize()
                    answered_correctly = get_score(
                        user_ellos_ellas, item.conjugation["ellos/ellas"]
                    )

                question_started = False

            # ===============================
            #    >>> RESUME PROGRESS <<<
            # ===============================
            progress.start()

            # ----- SAVE ATTEMPT -----
            crud.create_quiz_attempt(
                session_id=quiz_session.id,
                dictionary_id=item.text_id,
                answer=answer,
                answered_correctly=answered_correctly,
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
