"""Interactive batch quiz command backed by the Spanglish HTTP API."""

from time import monotonic

import questionary
from prompt_toolkit import prompt
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

from src.api_client import SpanglishAPIClient, SpanglishAPIError
from src.api_models import Attempt, QuizHistoryItem, QuizQuestion, QuizResult
from src.progressbars.quiz import quiz_progress
from src.utils import (
    confirm_with_quit,
    normalize_optional_id,
    optional_id_list,
    select_with_quit,
)

console = Console()


def _format_answer(
    answer: str | list[str] | dict[str, str] | dict[str, list[str]],
) -> str:
    """Format scalar and conjugation answers for the results table."""
    if isinstance(answer, str):
        return answer or "—"
    if isinstance(answer, list):
        return " / ".join(answer) or "—"
    return "\n".join(
        f"{key}: {' / '.join(value) if isinstance(value, list) else value}"
        for key, value in answer.items()
    ) or "—"


def _show_quiz_result(
    questions: list[QuizQuestion],
    attempts: list[Attempt],
    result: QuizResult,
    history: list[QuizHistoryItem] | None = None,
) -> None:
    """Render an authoritative per-question review and final guidance."""
    questions_by_id = {question.id: question for question in questions}
    answers_by_id = {attempt.question_id: attempt.answer for attempt in attempts}
    table = Table(
        title="Quiz Review",
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )
    table.add_column("#", justify="right", style="dim", no_wrap=True)
    table.add_column("Question", ratio=2)
    table.add_column("Your answer", ratio=2)
    table.add_column("Correct answer", ratio=2)
    table.add_column("Result", justify="center", no_wrap=True)

    for index, evaluation in enumerate(result.attempts, 1):
        question = questions_by_id.get(evaluation.question_id)
        status = Text(
            "✓ Correct" if evaluation.correct else "✗ Incorrect",
            style="bold green" if evaluation.correct else "bold red",
        )
        table.add_row(
            str(index),
            Text(question.prompt if question else evaluation.question_id),
            Text(_format_answer(answers_by_id.get(evaluation.question_id, ""))),
            Text(_format_answer(evaluation.accepted_answers)),
            status,
        )

    score_style = (
        "green"
        if result.score.percentage >= 80
        else "yellow"
        if result.score.percentage >= 60
        else "red"
    )
    advice = str(result.advice.get("summary", "Keep practising."))
    summary = Text()
    summary.append("Score: ", style="bold")
    summary.append(
        f"{result.score.correct}/{result.score.total} "
        f"({result.score.percentage:.2f}%)",
        style=f"bold {score_style}",
    )
    summary.append(
        f"\nCorrect: {result.score.correct}  •  Incorrect: {result.score.incorrect}"
    )
    summary.append("\n\nAdvice: ", style="bold")
    summary.append(advice)

    console.print()
    console.print(table)
    console.print(Panel(summary, title="Quiz Summary", border_style=score_style))
    _show_progress(history or [])


def _show_progress(history: list[QuizHistoryItem]) -> None:
    """Display recent scores chronologically and summarize their direction."""
    if not history:
        return
    chronological = list(reversed(history))
    table = Table(title="Last 5 Quiz Scores", header_style="bold magenta")
    table.add_column("Quiz", justify="right")
    table.add_column("Completed")
    table.add_column("Score", justify="right")
    table.add_column("Change", justify="right")
    previous = None
    for index, item in enumerate(chronological, 1):
        change = "—"
        change_style = "dim"
        if previous is not None:
            difference = item.percentage - previous
            change = f"{difference:+.2f}%"
            change_style = (
                "green"
                if difference > 0
                else "red"
                if difference < 0
                else "yellow"
            )
        table.add_row(
            str(index),
            item.completed_at.astimezone().strftime("%Y-%m-%d %H:%M"),
            f"{item.correct}/{item.total} ({item.percentage:.2f}%)",
            Text(change, style=change_style),
        )
        previous = item.percentage

    if len(chronological) == 1:
        trend = Text("Complete another quiz to start measuring progress.", style="cyan")
    else:
        difference = chronological[-1].percentage - chronological[0].percentage
        if difference > 0:
            trend = Text(
                f"↑ Improving: {difference:+.2f} percentage points",
                style="bold green",
            )
        elif difference < 0:
            trend = Text(
                f"↓ Recent decline: {difference:+.2f} percentage points",
                style="bold red",
            )
        else:
            trend = Text("→ Stable: no overall score change", style="bold yellow")
    console.print(table)
    console.print(Panel(trend, title="Progress", border_style=trend.style or "cyan"))


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
            select_with_quit("Select a category", category_choices)
        )
        chapter_choices = [questionary.Choice("All chapters", value="")] + [
            questionary.Choice(item.name, value=item.id) for item in options.chapters
        ]
        chapter_id = normalize_optional_id(
            select_with_quit("Select a chapter", chapter_choices)
        )
        source_id = select_with_quit(
            "Translate from",
            [
                questionary.Choice(item.name, value=item.id)
                for item in options.languages
            ],
        )
        target_languages = [item for item in options.languages if item.id != source_id]
        target_id = select_with_quit(
            "Translate to",
            [
                questionary.Choice(item.name, value=item.id)
                for item in target_languages
            ],
        )
        count = int(
            prompt("How many questions? ", default=str(options.default_question_count))
        )
        randomize = confirm_with_quit("Randomize selection?", default=True)
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
        history = client.list_quiz_results(limit=5)
        console.print("\n[bold green]Quiz completed.[/bold green]")
        _show_quiz_result(quiz.questions, attempts, result, history)
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
