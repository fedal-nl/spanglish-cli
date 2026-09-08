"""Interactive batch quiz command backed by the Spanglish HTTP API."""

from time import monotonic

import questionary
from prompt_toolkit import prompt
from rich.console import Console
from rich.progress import Progress

from src.api_client import SpanglishAPIClient, SpanglishAPIError
from src.api_models import Attempt, QuizQuestion
from src.progressbars.quiz import quiz_progress
from src.utils import normalize_optional_id, optional_id_list

console = Console()


def _matches(answer: str, accepted: list[str]) -> bool:
    """Provide immediate local feedback using the answers supplied by the API."""
    normalized = answer.strip().casefold().rstrip(".?!")
    return bool(normalized) and normalized in {
        value.strip().casefold().rstrip(".?!") for value in accepted
    }


def _ask_question(question: QuizQuestion) -> tuple[str | dict[str, str], bool]:
    """Ask a translation or every form of a conjugation question."""
    if question.type == "conjugation":
        accepted = question.accepted_answers
        if not isinstance(accepted, dict):
            return {}, False
        answers = {
            pronoun: prompt(f"{question.prompt} for '{pronoun}': ").strip()
            for pronoun in accepted
        }
        correct = all(
            _matches(answers[key], values) for key, values in accepted.items()
        )
        return answers, correct
    accepted = question.accepted_answers
    if not isinstance(accepted, list):
        return "", False
    answer = prompt(f"Translate '{question.prompt}': ").strip()
    return answer, _matches(answer, accepted)


def start(client: SpanglishAPIClient | None = None) -> None:
    """Fetch a complete quiz, run it locally, and submit all answers once."""
    owns_client = client is None
    client = client or SpanglishAPIClient()
    try:
        options = client.get_quiz_options()
        category_choices = [questionary.Choice("All", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.categories
        ]
        category_id = normalize_optional_id(
            questionary.select("Select a category", choices=category_choices).ask()
        )
        chapter_choices = [questionary.Choice("All chapters", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.chapters
        ]
        chapter_id = normalize_optional_id(
            questionary.select("Select a chapter", choices=chapter_choices).ask()
        )
        source_id = questionary.select(
            "Translate from",
            choices=[
                questionary.Choice(item.name, value=item.id)
                for item in options.languages
            ],
        ).ask()
        target_languages = [item for item in options.languages if item.id != source_id]
        target_id = questionary.select(
            "Translate to",
            choices=[
                questionary.Choice(item.name, value=item.id)
                for item in target_languages
            ],
        ).ask()
        count = int(
            prompt("How many questions? ", default=str(options.default_question_count))
        )
        randomize = questionary.confirm("Randomize selection?", default=True).ask()
        quiz = client.create_quiz(
            {
                "source_language_id": source_id,
                "target_language_id": target_id,
                "category_ids": optional_id_list(category_id),
                "chapter_ids": optional_id_list(chapter_id),
                "question_count": count,
                "selection_mode": "random" if randomize else "sequential",
                "question_types": ["translation", "conjugation"],
                "client_type": "cli",
            }
        )
        for warning in quiz.warnings:
            console.print(f"[yellow]{warning}[/yellow]")
        attempts = _run_questions(quiz.questions)
        result = client.submit_quiz(
            quiz.quiz_id,
            {
                "attempts": [item.model_dump(mode="json") for item in attempts],
                "client_type": "cli",
            },
        )
        console.print("\n[bold green]Quiz completed.[/bold green]")
        console.print(
            f"Score: {result.score.correct}/{result.score.total} "
            f"({result.score.percentage:.2f}%)"
        )
        console.print(f"Advice: {result.advice.get('summary', 'Keep practising.')}")
    except (SpanglishAPIError, ValueError) as exc:
        console.print(f"[red]{exc}[/red]")
    finally:
        if owns_client:
            client.close()


def _run_questions(questions: list[QuizQuestion]) -> list[Attempt]:
    """Collect all local answers while preserving response time metadata."""
    attempts = []
    with Progress(*quiz_progress, console=console) as progress:
        task = progress.add_task("Quiz Progress", total=len(questions))
        for index, question in enumerate(questions, 1):
            progress.stop()
            console.print(f"[yellow]Question {index} of {len(questions)}[/yellow]")
            started = monotonic()
            answer, correct = _ask_question(question)
            response_time_ms = round((monotonic() - started) * 1000)
            console.print(
                "[green]Correct![/green]" if correct else "[red]Incorrect![/red]"
            )
            progress.start()
            progress.update(task, advance=1)
            attempts.append(
                Attempt(
                    question_id=question.id,
                    answer=answer,
                    response_time_ms=response_time_ms,
                )
            )
    return attempts
