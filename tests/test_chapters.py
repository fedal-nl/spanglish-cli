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
        lambda message, values, default=None: 3,
    )
    monkeypatch.setattr(
        vocabulary.questionary, "select", lambda *args, **kwargs: Selection("")
    )
    answers = iter(["perro", "dog"])
    monkeypatch.setattr(vocabulary, "prompt", lambda *args, **kwargs: next(answers))
    assert vocabulary._build_payload(options())["chapter_id"] is None


def test_create_chapter_delegates_to_api(monkeypatch) -> None:
    client = SimpleNamespace(
        create_chapter=lambda name: SimpleNamespace(id=5, name=name)
    )
    monkeypatch.setattr(vocabulary, "prompt", lambda _message: "Chapter 1")
    vocabulary.create_chapter(client)


def test_create_category_delegates_to_api(monkeypatch) -> None:
    client = SimpleNamespace(
        create_category=lambda name: SimpleNamespace(id=6, name=name)
    )
    monkeypatch.setattr(vocabulary, "prompt", lambda _message: "Connectors")
    vocabulary.create_category(client)


def test_add_vocabulary_reuses_context_for_batch(monkeypatch) -> None:
    selections = []

    def select_id(message, values, default=None):
        selections.append(message)
        return 3

    monkeypatch.setattr(vocabulary, "_select_id", select_id)
    monkeypatch.setattr(vocabulary, "select_with_quit", lambda *args, **kwargs: 5)
    confirmations = iter([False, True, False, False])
    monkeypatch.setattr(
        vocabulary,
        "confirm_with_quit",
        lambda *args, **kwargs: next(confirmations),
    )
    answers = iter(["perro", "dog", "gato", "cat"])
    monkeypatch.setattr(vocabulary, "prompt", lambda *args, **kwargs: next(answers))
    payloads = []
    client = SimpleNamespace(
        get_quiz_options=options,
        create_vocabulary=lambda payload: payloads.append(payload)
        or SimpleNamespace(
            text=payload["text"],
            translations=[
                SimpleNamespace(translation=payload["translations"][0]["text"])
            ],
        ),
    )

    vocabulary.add_vocabulary(client)

    assert selections == ["Select a category"]
    assert [payload["text"] for payload in payloads] == ["perro", "gato"]
    assert all(payload["category_ids"] == [3] for payload in payloads)
    assert all(payload["chapter_id"] == 5 for payload in payloads)
