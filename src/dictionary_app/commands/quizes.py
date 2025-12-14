from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import choice
from rich.console import Console
from rich.progress import Progress

from src.db import crud
from src.dictionary_app.commands.quiz.factory import convert_dictionary_to_quiz_item
from src.dictionary_app.commands.quiz.questions import ask_question
from src.enums import CategoryEnum, LanguageEnum
from src.progressbars.quiz import quiz_progress
from src.utils import BOOLEAN_CHOICES

console = Console()

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

    limit = prompt("How many records ? ", default="10")
    is_random = prompt("Randomize selection [y/N]?", default="y").strip().lower() in ("y", "yes")

    quiz_session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID:[/] {quiz_session.id}")

    # ---------- LOAD QUIZ ITEMS ----------
    rows = crud.list_dictionary_entries(
        category=category,
        limit=int(limit),
        is_random=BOOLEAN_CHOICES.get(is_random, False)
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
            answer = ""

            console.print("[yellow]Take your time to think...[/yellow]")

            answer, answered_correctly = ask_question(item, language)
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
