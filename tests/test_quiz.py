"""Unit tests for client-side quiz interaction helpers."""

from io import StringIO

import questionary
from rich.console import Console

from src.api_models import Attempt, QuizHistoryItem, QuizQuestion, QuizResult
from src.dictionary_app.commands import quizes
from src.utils import normalize_optional_id, optional_id_list


def test_matches_is_exact_and_case_insensitive() -> None:
    """Allow harmless formatting but reject the old substring behavior."""
    assert quizes._matches(" DOG. ", ["dog"])
    assert not quizes._matches("do", ["dog"])
    assert not quizes._matches("", ["dog"])


def test_all_optional_id_values_are_normalized() -> None:
    """Never send display labels from an All selection to the API."""
    all_choice = questionary.Choice("All", value="")
    assert all_choice.value == ""
    assert normalize_optional_id(all_choice.value) is None
    for value in (None, "", "  ", "All", "all", "ALL", "None"):
        assert normalize_optional_id(value) is None
    assert normalize_optional_id("42") == 42
    assert normalize_optional_id(42) == 42
    assert optional_id_list("All") == []
    assert optional_id_list(42) == [42]


def test_ask_translation_question(monkeypatch) -> None:
    """Collect and locally evaluate a translation response."""
    monkeypatch.setattr(quizes, "prompt", lambda message: "dog")
    question = QuizQuestion(
        id="translation-7",
        vocabulary_id=7,
        type="translation",
        prompt="perro",
        accepted_answers=["dog"],
        category_ids=[4],
    )
    assert quizes._ask_question(question) == ("dog", True)


def test_ask_conjugation_question(monkeypatch) -> None:
    """Collect every pronoun form into the batch submission shape."""
    answers = iter(["hablo", "hablas"])
    monkeypatch.setattr(quizes, "prompt", lambda message: next(answers))
    question = QuizQuestion(
        id="conjugation-8",
        vocabulary_id=8,
        type="conjugation",
        prompt="Conjugate hablar",
        accepted_answers={"yo": ["hablo"], "tú": ["hablas"]},
        category_ids=[2],
    )
    submitted, correct = quizes._ask_question(question)
    assert submitted == {"yo": "hablo", "tú": "hablas"}
    assert correct


def test_show_quiz_result_renders_authoritative_review(monkeypatch) -> None:
    """Show each answer, accepted correction, score, and API advice."""
    output = StringIO()
    monkeypatch.setattr(
        quizes,
        "console",
        Console(file=output, force_terminal=False, color_system=None, width=180),
    )
    questions = [
        QuizQuestion(
            id="translation-7",
            vocabulary_id=7,
            type="translation",
            prompt="perro",
            accepted_answers=["dog"],
            category_ids=[4],
        ),
        QuizQuestion(
            id="conjugation-8",
            vocabulary_id=8,
            type="conjugation",
            prompt="Conjugate hablar",
            accepted_answers={"yo": ["hablo"], "tú": ["hablas"]},
            category_ids=[2],
        ),
    ]
    attempts = [
        Attempt(question_id="translation-7", answer="cat"),
        Attempt(
            question_id="conjugation-8",
            answer={"yo": "hablo", "tú": "hablas"},
        ),
    ]
    result = QuizResult.model_validate(
        {
            "result_id": 10,
            "quiz_id": 5,
            "score": {
                "correct": 1,
                "incorrect": 1,
                "total": 2,
                "percentage": 50,
            },
            "attempts": [
                {
                    "question_id": "translation-7",
                    "correct": False,
                    "score": 0,
                    "accepted_answers": ["dog"],
                    "feedback": "Review this translation.",
                },
                {
                    "question_id": "conjugation-8",
                    "correct": True,
                    "score": 1,
                    "accepted_answers": {"yo": ["hablo"], "tú": ["hablas"]},
                    "feedback": "Well done.",
                },
            ],
            "advice": {"summary": "Review incorrect answers and try again."},
        }
    )

    history = [
        QuizHistoryItem(
            quiz_id=5,
            completed_at="2026-09-03T10:00:00Z",
            correct=1,
            total=2,
            percentage=50,
        ),
        QuizHistoryItem(
            quiz_id=4,
            completed_at="2026-09-02T10:00:00Z",
            correct=1,
            total=4,
            percentage=25,
        ),
    ]
    quizes._show_quiz_result(questions, attempts, result, history)

    rendered = output.getvalue()
    for expected in (
        "Quiz Review",
        "perro",
        "cat",
        "dog",
        "✗ Incorrect",
        "Conjugate hablar",
        "yo: hablo",
        "✓ Correct",
        "Score: 1/2 (50.00%)",
        "Advice: Review incorrect answers and try again.",
        "Last 5 Quiz Scores",
        "+25.00%",
        "Improving: +25.00 percentage points",
    ):
        assert expected in rendered
    assert "Feedback" not in rendered
    assert "Review this translation." not in rendered
