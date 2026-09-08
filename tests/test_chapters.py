"""Chapter command and optional vocabulary-assignment tests."""

from types import SimpleNamespace

from src.api_models import QuizOptions
from src.dictionary_app.commands import vocabulary


def options() -> QuizOptions:
    return QuizOptions.model_validate(
        {
            "languages": [
                {"id": 1, "name": "Spanish", "code": "es"},
                {"id": 2, "name": "English", "code": "en"},
            ],
            "categories": [{"id": 3, "name": "Animals"}],
            "chapters": [{"id": 5, "name": "Chapter 1"}],
            "vocabulary_types": [{"id": 4, "name": "Word"}],
            "selection_modes": ["random"],
            "question_types": ["translation"],
            "default_question_count": 10,
            "maximum_question_count": 100,
        }
    )


class Selection:
    def __init__(self, value):
        self.value = value

    def ask(self):
        return self.value


def test_vocabulary_chapter_is_optional(monkeypatch) -> None:
    monkeypatch.setattr(
        vocabulary,
        "_select_id",
        lambda message, values, default=None: 3 if "category" in message else 4,
    )
    monkeypatch.setattr(
        vocabulary.questionary, "select", lambda *args, **kwargs: Selection("")
    )
    answers = iter(["perro", "dog", "N"])
    monkeypatch.setattr(vocabulary, "prompt", lambda *args, **kwargs: next(answers))
    assert vocabulary._build_payload(options())["chapter_id"] is None


def test_create_chapter_delegates_to_api(monkeypatch) -> None:
    client = SimpleNamespace(
        create_chapter=lambda name: SimpleNamespace(id=5, name=name)
    )
    monkeypatch.setattr(vocabulary, "prompt", lambda _message: "Chapter 1")
    vocabulary.create_chapter(client)
