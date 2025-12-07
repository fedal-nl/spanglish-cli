import questionary
import typer
from rich.console import Console
from rich.progress import Progress

from src.commands.quiz.factory import (
    convert_sentence_to_quiz_item,
    convert_word_to_quiz_item,
)
from src.db import crud
from src.enums import CategoryEnum, LanguageEnum, QuizContentTypeEnum, TopicEnum
from src.progressbars.quiz import quiz_progress

app = typer.Typer(
    add_completion=False,
    help="🎯 Quiz commands: start quizzes and view performance."
)
console = Console()

@app.command()
def start():
    """Start a quiz session..."""

    # ---------- INITIAL USER PROMPTS ----------
    quiz_type = questionary.select(
        "Select quiz type",
        choices=QuizContentTypeEnum
    ).ask()

    with_category = typer.confirm(
            "Do you want to filter by Category ?", default=False
        )

    category = None
    if with_category:
        if quiz_type == QuizContentTypeEnum.WORD:
            category = questionary.select(
                "Select a category",
                choices=CategoryEnum
            ).ask()
        else:
            category = questionary.select(
                "Select a topic",
                choices=TopicEnum
            ).ask()

    language =  questionary.select(
        "Select a language",
        choices=LanguageEnum,
    ).ask()

    limit = typer.prompt("How many records ?", default=10, type=int)
    is_random = typer.confirm("Randomize selection ?", default=True)

    quiz_session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID:[/] {quiz_session.id}")

    rows = [] # To hold quiz items depending on type
    # ---------- LOAD QUIZ ITEMS ----------
    if quiz_type == QuizContentTypeEnum.WORD:
        rows = crud.list_words(category=category, limit=limit, is_random=is_random)
    else:
        rows = crud.list_sentences(topic=category, limit=limit, is_random=is_random)
    # ------------------------------------------

    quiz_items = []
    if quiz_type == QuizContentTypeEnum.WORD:
        quiz_items = [convert_word_to_quiz_item(w, language) for w in rows]
    else:
        quiz_items = [convert_sentence_to_quiz_item(s, language) for s in rows]

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
            # If the selected language is English, the question will be shown in English
            # ----- SHOW HINT IF Spanish -----
            if language == LanguageEnum.ENGLISH:
                question = item.question
                console.print(f"\n[bold blue]Translate to Spanish:[/] {question}")

                answer = typer.prompt("Enter the translation").strip().lower()
                answered_correctly = False

                if answer == item.answer.lower():
                    answered_correctly = True
            else:
                # ----- ASK THE QUESTION -----
                console.print(f"\n[bold blue]Word:[/] {item.question} ({item.category})")
                answer = typer.prompt("Enter the translation").strip().lower()
                answered_correctly = False

                if answer == item.answer.lower():
                    answered_correctly = True

            # Verb conjugation section
            if item.conjugation:
                console.print("[bold blue]Now conjugate the verb:[/bold blue]")

                user_yo = typer.prompt("yo").strip().capitalize()
                user_tu = typer.prompt("tu").strip().capitalize()
                user_ella_el = typer.prompt("ella/el").strip().capitalize()
                user_nosotros = typer.prompt("nosotros").strip().capitalize()
                user_vosotros = typer.prompt("vosotros").strip().capitalize()
                user_ellos_ellas = typer.prompt("ellos_ellas").strip().capitalize()

                if not (
                    user_yo == item.conjugation["yo"] and
                    user_tu == item.conjugation["tú"] and
                    user_ella_el == item.conjugation["él/ella"] and
                    user_nosotros == item.conjugation["nosotros"] and
                    user_vosotros == item.conjugation["vosotros"] and
                    user_ellos_ellas == item.conjugation["ellos/ellas"]
                ):
                    answered_correctly = False

            # ===============================
            #    >>> RESUME PROGRESS <<<
            # ===============================
            progress.start()

            # ----- SAVE ATTEMPT -----
            crud.create_quiz_attempt(
                session_id=quiz_session.id,
                content_type=item.content_type,
                content_id=item.content_type_id,
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
