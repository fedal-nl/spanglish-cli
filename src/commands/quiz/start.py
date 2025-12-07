import questionary
import typer
from rich.console import Console

from src.commands.quiz.services.loader import load_quiz_items
from src.commands.quiz.services.progress import quiz_progress_context
from src.commands.quiz.services.scores import show_summary
from src.commands.quiz.services.sentences import ask_sentence_question
from src.commands.quiz.services.words import ask_word_question
from src.db import crud
from src.enums import CategoryEnum, LanguageEnum, QuizContentTypeEnum

app = typer.Typer(help="🎯 Start a quiz session.")
console = Console()


@app.command()
def start():
    """Start a quiz session for Words or Sentences."""

    # Create session
    session = crud.create_quiz_session()
    console.print(f"[green]Quiz session started with ID {session.id}[/green]\n")

    # Select quiz type
    content_type = questionary.select(
        "What do you want to practice?",
        choices=QuizContentTypeEnum,
    ).ask()

    # Select translation direction
    language = questionary.select(
        "Translate to which language?",
        choices=LanguageEnum,
    ).ask()

    # Optional word category filter
    category = None
    if content_type == QuizContentTypeEnum.WORD:
        if typer.confirm("Filter by category?", default=False):
            category = questionary.select(
                "Select category",
                choices=CategoryEnum,
            ).ask()

    # Limit
    limit = typer.prompt("How many items?", default=10, type=int)

    # Load quiz items
    items = load_quiz_items(content_type, limit, category)

    correct = 0
    incorrect = 0

    # Quiz loop with progress
    with quiz_progress_context(total=len(items), console=console) as quiz_progress:

        for index, item in enumerate(items, start=1):
            quiz_progress.update_question(index)

            quiz_progress.stop()

            if content_type == QuizContentTypeEnum.WORD:
                answered_correctly = ask_word_question(item, language)
            else:
                answered_correctly = ask_sentence_question(item, language)

            # Save attempt
            crud.create_quiz_attempt(
                session_id=session.id,
                content_type=content_type,
                content_id=item.id,
                answered_correctly=answered_correctly,
            )

            correct += int(answered_correctly)
            incorrect += int(not answered_correctly)

            quiz_progress.advance()

    # Final summary
    show_summary(correct, incorrect, len(items))
