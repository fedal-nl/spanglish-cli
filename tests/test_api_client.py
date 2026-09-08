"""Unit tests for the versioned Spanglish HTTP client."""

import httpx
import pytest

from src.api_client import SpanglishAPIClient, SpanglishAPIError

VOCABULARY = {
    "id": 7,
    "text": "perro",
    "language": {"id": 1, "name": "Spanish", "code": "es"},
    "vocabulary_type": {"id": 3, "name": "Word"},
    "chapter": None,
    "categories": [{"id": 4, "name": "Animals"}],
    "translations": [{"id": 8, "language_id": 2, "translation": "dog"}],
    "verb_conjugations": [],
    "created_at": "2026-09-03T10:00:00Z",
}


def response_for(request: httpx.Request) -> httpx.Response:
    """Return representative backend responses for every client operation."""
    path = request.url.path
    if path.endswith("/quiz-options"):
        return httpx.Response(
            200,
            json={
                "languages": [
                    {"id": 1, "name": "Spanish", "code": "es"},
                    {"id": 2, "name": "English", "code": "en"},
                ],
                "categories": [{"id": 4, "name": "Animals", "available_questions": 1}],
                "chapters": [{"id": 5, "name": "Chapter 1"}],
                "vocabulary_types": [{"id": 3, "name": "Word"}],
                "selection_modes": ["random", "sequential"],
                "question_types": ["translation", "conjugation"],
                "default_question_count": 10,
                "maximum_question_count": 100,
            },
        )
    if path.endswith("/quizzes/9/results"):
        return httpx.Response(
            200,
            json={
                "result_id": 9,
                "quiz_id": 9,
                "score": {"correct": 1, "incorrect": 0, "total": 1, "percentage": 100},
                "attempts": [],
                "advice": {"summary": "Strong result."},
            },
        )
    if path.endswith("/quizzes"):
        return httpx.Response(
            201,
            json={
                "quiz_id": 9,
                "generated_at": "2026-09-03T10:00:00Z",
                "requested_question_count": 1,
                "actual_question_count": 1,
                "configuration": {},
                "warnings": [],
                "questions": [
                    {
                        "id": "translation-7",
                        "vocabulary_id": 7,
                        "type": "translation",
                        "prompt": "perro",
                        "accepted_answers": ["dog"],
                        "category_ids": [4],
                    }
                ],
            },
        )
    if path.endswith("/vocabulary") and request.method == "GET":
        assert "language_id" not in request.url.params
        assert "category_id" not in request.url.params
        assert "chapter_id" not in request.url.params
        assert request.url.params["randomize"] == "false"
        return httpx.Response(
            200, json={"items": [VOCABULARY], "total": 1, "page": 1, "page_size": 10}
        )
    if path.endswith("/chapters"):
        if request.method == "GET":
            return httpx.Response(200, json=[{"id": 5, "name": "Chapter 1"}])
        return httpx.Response(201, json={"id": 5, "name": "Chapter 1"})
    if path.endswith("/vocabulary/7") and request.method == "DELETE":
        return httpx.Response(204)
    return httpx.Response(
        200 if request.method in {"GET", "PUT"} else 201, json=VOCABULARY
    )


def test_client_supports_crud_and_quiz_lifecycle() -> None:
    """Validate every API operation into its Pydantic response model."""
    with SpanglishAPIClient(
        base_url="https://example.test/api/v1/spanglish",
        transport=httpx.MockTransport(response_for),
    ) as client:
        assert client.get_quiz_options().languages[0].code == "es"
        assert client.list_chapters()[0].name == "Chapter 1"
        assert client.create_chapter("Chapter 1").id == 5
        assert client.list_vocabulary(
            page_size=10,
            language_id="All",
            category_id="all",
            chapter_id="All",
        ).items[0].text == "perro"
        assert client.get_vocabulary(7).id == 7
        assert client.create_vocabulary({}).id == 7
        assert client.update_vocabulary(7, {}).id == 7
        assert client.delete_vocabulary(7) is None
        quiz = client.create_quiz({})
        assert quiz.questions[0].accepted_answers == ["dog"]
        assert client.submit_quiz(9, {}).score.percentage == 100


def test_client_translates_api_and_network_errors() -> None:
    """Expose concise terminal-safe errors instead of httpx exceptions."""

    def api_error(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Vocabulary not found"})

    client = SpanglishAPIClient(transport=httpx.MockTransport(api_error))
    with pytest.raises(SpanglishAPIError, match="Vocabulary not found"):
        client.get_vocabulary(99)
    client.close()

    def network_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = SpanglishAPIClient(transport=httpx.MockTransport(network_error))
    with pytest.raises(SpanglishAPIError, match="Could not connect"):
        client.get_quiz_options()
    client.close()
