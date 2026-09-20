"""Unit tests for the versioned Spanglish HTTP client."""

from types import SimpleNamespace

import httpx
import pytest
from r2d2_sdk import MemoryTokenStore, TokenPair

from src.api_client import SpanglishAPIClient, SpanglishAPIError

VOCABULARY = {
    "id": 7,
    "text": "perro",
    "language": {"id": 1, "name": "Spanish", "code": "es"},
    "chapter": None,
    "categories": [{"id": 4, "name": "Animals"}],
    "translations": [{"id": 8, "language_id": 2, "translation": "dog"}],
    "verb_conjugations": [],
    "created_at": "2026-09-03T10:00:00Z",
}
USER = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "learner",
    "email": "learner@example.com",
    "avatar_url": None,
    "is_active": True,
    "last_login_at": None,
    "created_at": "2026-09-03T10:00:00Z",
}


def response_for(request: httpx.Request) -> httpx.Response:  # noqa: C901
    """Return representative backend responses for every client operation."""
    path = request.url.path
    if path == "/health":
        return httpx.Response(200, json={"status": "ok"})
    if path.endswith("/auth/me"):
        return httpx.Response(200, json=USER)
    if path.endswith("/auth/login"):
        return httpx.Response(
            200,
            json={
                "access_token": "new-access-token",
                "refresh_token": "n" * 40,
                "token_type": "bearer",
                "expires_in": 900,
            },
        )
    if path.endswith("/auth/register"):
        return httpx.Response(201, json=USER)
    if path.endswith("/auth/password-reset/request"):
        return httpx.Response(202, json={"message": "If the account exists"})
    if path.endswith("/auth/password-reset/confirm"):
        return httpx.Response(204)
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
    if path.endswith("/quizzes/results"):
        assert request.url.params["limit"] == "5"
        return httpx.Response(
            200,
            json=[
                {
                    "quiz_id": 9,
                    "completed_at": "2026-09-03T10:00:00Z",
                    "correct": 1,
                    "total": 1,
                    "percentage": 100,
                }
            ],
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
    if path.endswith("/artists"):
        return httpx.Response(
            200 if request.method == "GET" else 201,
            json=[{"id": 7, "name": "Singer"}]
            if request.method == "GET"
            else {"id": 7, "name": "Singer"},
        )
    if path.endswith("/songs"):
        song = {"id": 9, "title": "Title", "artist": {"id": 7, "name": "Singer"}}
        return httpx.Response(
            200 if request.method == "GET" else 201,
            json=[song] if request.method == "GET" else song,
        )
    if path.endswith("/categories"):
        assert request.method == "POST"
        assert request.read() == b'{"name":"Connectors"}'
        return httpx.Response(201, json={"id": 6, "name": "Connectors"})
    if path.endswith("/vocabulary/7") and request.method == "DELETE":
        return httpx.Response(204)
    return httpx.Response(
        200 if request.method in {"GET", "PUT"} else 201, json=VOCABULARY
    )


def test_client_supports_crud_and_quiz_lifecycle() -> None:
    """Validate every API operation into its Pydantic response model."""
    token_store = MemoryTokenStore()
    token_store.save(
        TokenPair(
            access_token="access-token",
            refresh_token="r" * 40,
            token_type="bearer",
            expires_in=900,
        )
    )
    with SpanglishAPIClient(
        base_url="https://example.test/api/v1/spanglish",
        transport=httpx.MockTransport(response_for),
        token_store=token_store,
    ) as client:
        client.check_connection()
        assert client.check_authentication() == "learner@example.com"
        assert (
            client.register("learner", "learner@example.com", "secret-password")
            == "learner@example.com"
        )
        assert client.login("learner@example.com", "secret") == "learner@example.com"
        client.request_password_reset("learner@example.com")
        client.confirm_password_reset("t" * 32, "new-password")
        assert (
            client.login("learner@example.com", "new-password") == "learner@example.com"
        )
        assert client.get_quiz_options().languages[0].code == "es"
        assert client.create_category("Connectors").name == "Connectors"
        assert client.list_chapters()[0].name == "Chapter 1"
        assert client.create_chapter("Chapter 1").id == 5
        assert client.list_artists()[0].id == 7
        assert client.create_artist("Singer").id == 7
        assert client.list_songs(7)[0].id == 9
        assert client.create_song("Title", 7).id == 9
        assert (
            client.list_vocabulary(
                page_size=10,
                language_id="All",
                category_id="all",
                chapter_id="All",
            )
            .items[0]
            .text
            == "perro"
        )
        assert client.get_vocabulary(7).id == 7
        assert client.create_vocabulary({}).id == 7
        assert client.update_vocabulary(7, {}).id == 7
        assert client.delete_vocabulary(7) is None
        quiz = client.create_quiz({})
        assert quiz.questions[0].accepted_answers == ["dog"]
        assert client.submit_quiz(9, {}).score.percentage == 100
        assert client.list_quiz_results(limit=5)[0].quiz_id == 9


def test_client_translates_api_and_network_errors() -> None:
    """Expose concise terminal-safe errors instead of httpx exceptions."""

    def api_error(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Vocabulary not found"})

    token_store = MemoryTokenStore()
    token_store.save(
        TokenPair(
            access_token="access-token",
            refresh_token="r" * 40,
            token_type="bearer",
            expires_in=900,
        )
    )
    client = SpanglishAPIClient(
        transport=httpx.MockTransport(api_error), token_store=token_store
    )
    with pytest.raises(SpanglishAPIError, match="Vocabulary not found"):
        client.get_vocabulary(99)
    client.close()

    def network_error(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = SpanglishAPIClient(
        transport=httpx.MockTransport(network_error), token_store=token_store
    )
    with pytest.raises(SpanglishAPIError, match="Could not connect"):
        client.get_quiz_options()
    client.close()


def test_health_check_rejects_unhealthy_response() -> None:
    client = SpanglishAPIClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, json={"status": "degraded"})
        )
    )
    with pytest.raises(SpanglishAPIError, match="unhealthy status"):
        client.check_connection()
    client.close()


def test_password_reset_supports_older_sdk_clients() -> None:
    token_store = MemoryTokenStore()
    token_store.save(
        TokenPair.model_validate(
            {
                "access_token": "access-token",
                "refresh_token": "r" * 40,
                "token_type": "bearer",
                "expires_in": 900,
            }
        )
    )
    client = SpanglishAPIClient(
        base_url="https://example.test/api/v1/spanglish",
        transport=httpx.MockTransport(response_for),
    )
    client._auth = SimpleNamespace(
        token_store=token_store,
        close=lambda: None,
    )

    client.request_password_reset("learner@example.com")
    client.confirm_password_reset("t" * 32, "new-password")

    assert token_store.load() is None
    client.close()
