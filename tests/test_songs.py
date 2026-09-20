"""Song-category selection and creation tests."""

from types import SimpleNamespace

from src.api_models import QuizOptions
from src.dictionary_app.commands import vocabulary


def song_options() -> QuizOptions:
    return QuizOptions.model_validate(
        {
            "languages": [
                {"id": 1, "name": "Spanish", "code": "es"},
                {"id": 2, "name": "English", "code": "en"},
            ],
            "categories": [{"id": 3, "name": "Songs"}],
            "chapters": [],
            "selection_modes": ["random"],
            "question_types": ["translation"],
            "default_question_count": 10,
            "maximum_question_count": 100,
        }
    )


def test_song_context_selects_existing_song(monkeypatch) -> None:
    client = SimpleNamespace(
        list_artists=lambda: [SimpleNamespace(id=7, name="Singer")],
        list_songs=lambda artist_id: [SimpleNamespace(id=9, title="Title")],
    )
    choices = iter([7, 9])
    prompts = []
    monkeypatch.setattr(
        vocabulary,
        "_select_id",
        lambda *args, **kwargs: prompts.append("Select a category") or 3,
    )
    monkeypatch.setattr(
        vocabulary,
        "select_with_quit",
        lambda message, *args, **kwargs: prompts.append(message) or next(choices),
    )
    context = vocabulary._select_vocabulary_context(song_options(), client=client)
    assert context.song_id == 9
    assert prompts == ["Select a category", "Select an artist", "Select a song"]
    assert context.chapter_id is None


def test_song_context_creates_artist_and_song(monkeypatch) -> None:
    created = []
    client = SimpleNamespace(
        list_artists=lambda: [],
        create_artist=lambda name: created.append(("artist", name))
        or SimpleNamespace(id=7),
        list_songs=lambda artist_id: [],
        create_song=lambda title, artist_id: created.append(("song", title, artist_id))
        or SimpleNamespace(id=9),
    )
    choices = iter(["new", "new"])
    answers = iter(["Singer", "Title"])
    monkeypatch.setattr(vocabulary, "_select_id", lambda *args, **kwargs: 3)
    monkeypatch.setattr(
        vocabulary, "select_with_quit", lambda *args, **kwargs: next(choices)
    )
    monkeypatch.setattr(vocabulary, "prompt", lambda *args, **kwargs: next(answers))
    context = vocabulary._select_vocabulary_context(song_options(), client=client)
    assert context.song_id == 9
    assert created == [("artist", "Singer"), ("song", "Title", 7)]


def test_lyrics_batch_reuses_selected_song(monkeypatch) -> None:
    """Adding another lyric keeps the artist/song context selected once."""
    selections = []
    client = SimpleNamespace(
        get_quiz_options=song_options,
        list_artists=lambda: [SimpleNamespace(id=7, name="Singer")],
        list_songs=lambda artist_id: [SimpleNamespace(id=9, title="Title")],
    )
    choices = iter([7, 9])
    answers = iter(["primera", "first", "segunda", "second"])
    confirmations = iter([False, True, False, False])
    payloads = []
    client.create_vocabulary = lambda payload: payloads.append(
        payload
    ) or SimpleNamespace(
        text=payload["text"],
        translations=[SimpleNamespace(translation=payload["translations"][0]["text"])],
    )
    monkeypatch.setattr(
        vocabulary,
        "_select_id",
        lambda *args, **kwargs: selections.append("category") or 3,
    )
    monkeypatch.setattr(
        vocabulary, "select_with_quit", lambda *args, **kwargs: next(choices)
    )
    monkeypatch.setattr(vocabulary, "prompt", lambda *args, **kwargs: next(answers))
    monkeypatch.setattr(
        vocabulary, "confirm_with_quit", lambda *args, **kwargs: next(confirmations)
    )

    vocabulary.add_vocabulary(client)

    assert selections == ["category"]
    assert [item["song_id"] for item in payloads] == [9, 9]
    assert [item["text"] for item in payloads] == ["primera", "segunda"]
