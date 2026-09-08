"""Synchronous HTTP client used by the interactive Spanglish CLI."""

from typing import Any

import httpx

from src.api_models import (
    Quiz,
    QuizOptions,
    QuizResult,
    Reference,
    Vocabulary,
    VocabularyPage,
)
from src.settings import API_TIMEOUT_SECONDS, SPANGLISH_API_URL
from src.utils import normalize_optional_id


class SpanglishAPIError(RuntimeError):
    """Describe a connection or API response failure in CLI-friendly language."""


class SpanglishAPIClient:
    """Expose version 1 Spanglish endpoints as typed Python operations."""

    def __init__(
        self,
        base_url: str = SPANGLISH_API_URL,
        timeout: float = API_TIMEOUT_SECONDS,
        transport: httpx.BaseTransport | None = None,
    ):
        """Create a reusable HTTP client for the configured API URL."""
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"), timeout=timeout, transport=transport
        )

    def __enter__(self) -> "SpanglishAPIClient":
        """Return this client when used as a context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Close network resources when leaving a context manager."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def get_quiz_options(self) -> QuizOptions:
        """Fetch languages, categories, content types, and quiz modes."""
        return QuizOptions.model_validate(self._request("GET", "/quiz-options"))

    def list_chapters(self) -> list[Reference]:
        """Fetch chapters available for vocabulary and quizzes."""
        return [
            Reference.model_validate(item)
            for item in self._request("GET", "/chapters")
        ]

    def create_chapter(self, name: str) -> Reference:
        """Create a chapter through the shared API."""
        return Reference.model_validate(
            self._request("POST", "/chapters", json={"name": name})
        )

    def list_vocabulary(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        language_id: int | str | None = None,
        category_id: int | str | None = None,
        chapter_id: int | str | None = None,
        search: str | None = None,
        randomize: bool = False,
    ) -> VocabularyPage:
        """Fetch a filtered page of vocabulary cards."""
        optional_params = {
            "page": page,
            "page_size": page_size,
            "language_id": normalize_optional_id(language_id),
            "category_id": normalize_optional_id(category_id),
            "chapter_id": normalize_optional_id(chapter_id),
            "search": search,
            "randomize": randomize,
        }
        params = {
            key: value
            for key, value in optional_params.items()
            if value is not None
        }
        return VocabularyPage.model_validate(
            self._request("GET", "/vocabulary", params=params)
        )

    def get_vocabulary(self, vocabulary_id: int) -> Vocabulary:
        """Fetch one complete vocabulary card."""
        return Vocabulary.model_validate(
            self._request("GET", f"/vocabulary/{vocabulary_id}")
        )

    def create_vocabulary(self, payload: dict[str, Any]) -> Vocabulary:
        """Create vocabulary with translations and optional conjugations."""
        return Vocabulary.model_validate(
            self._request("POST", "/vocabulary", json=payload)
        )

    def update_vocabulary(
        self, vocabulary_id: int, payload: dict[str, Any]
    ) -> Vocabulary:
        """Replace an existing vocabulary card."""
        return Vocabulary.model_validate(
            self._request("PUT", f"/vocabulary/{vocabulary_id}", json=payload)
        )

    def delete_vocabulary(self, vocabulary_id: int) -> None:
        """Delete a vocabulary card and all cascading child records."""
        self._request("DELETE", f"/vocabulary/{vocabulary_id}")

    def create_quiz(self, payload: dict[str, Any]) -> Quiz:
        """Fetch a complete quiz matching the user's selected options."""
        return Quiz.model_validate(self._request("POST", "/quizzes", json=payload))

    def submit_quiz(self, quiz_id: int, payload: dict[str, Any]) -> QuizResult:
        """Submit all local answers and return the authoritative result."""
        return QuizResult.model_validate(
            self._request("POST", f"/quizzes/{quiz_id}/results", json=payload)
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Send a request and translate HTTP/network errors for terminal display."""
        try:
            response = self._client.request(method, path, **kwargs)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                detail = exc.response.json().get("detail", exc.response.text)
            except ValueError:
                detail = exc.response.text
            raise SpanglishAPIError(
                f"API returned {exc.response.status_code}: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise SpanglishAPIError(
                f"Could not connect to the Spanglish API: {exc}"
            ) from exc
        if response.status_code == 204 or not response.content:
            return None
        return response.json()
