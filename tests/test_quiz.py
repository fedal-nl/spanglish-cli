"""Unit tests for client-side quiz interaction helpers."""

import questionary

from src.api_models import QuizQuestion
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
