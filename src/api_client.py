"""Synchronous HTTP client used by the interactive Spanglish CLI."""

from typing import Any

import httpx
from pydantic import ValidationError
from r2d2_sdk import FileTokenStore, R2D2Client, R2D2Error, TokenStore

from src.api_models import (
    Quiz,
    QuizHistoryItem,
    QuizOptions,
    QuizResult,
    Reference,
    Song,
    Vocabulary,
    VocabularyPage,
)
from src.settings import API_TIMEOUT_SECONDS, SPANGLISH_API_URL, TOKEN_STORE_PATH
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
        token_store: TokenStore | None = None,
    ):
        """Create a reusable HTTP client for the configured API URL."""
        normalized = base_url.rstrip("/")
        auth_url = normalized.removesuffix("/spanglish")
        server_url = auth_url.removesuffix("/api/v1")
        self._auth = R2D2Client(
            auth_url,
            token_store=token_store or FileTokenStore(TOKEN_STORE_PATH),
            timeout=timeout,
            transport=transport,
        )
        self._health = httpx.Client(
            base_url=server_url, timeout=timeout, transport=transport
        )
        print(
            f"SpanglishAPIClient initialized with base_url={base_url}, "
            f"timeout={timeout}"
        )

    def __enter__(self) -> "SpanglishAPIClient":
        """Return this client when used as a context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Close network resources when leaving a context manager."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._auth.close()
        self._health.close()

    def check_connection(self) -> None:
        """Verify that the configured R2D2 server is reachable and healthy."""
        try:
            response = self._health.get("/health")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SpanglishAPIError(f"Could not connect to the API: {exc}") from exc
        try:
            status = response.json().get("status")
        except ValueError as exc:
            raise SpanglishAPIError("The API health response is invalid") from exc
        if status != "ok":
            raise SpanglishAPIError(f"The API reported an unhealthy status: {status}")

    def check_authentication(self) -> str:
        """Validate stored credentials and return the authenticated identity."""
        try:
            user = self._auth.me()
        except (R2D2Error, httpx.HTTPError, ValidationError) as exc:
            raise SpanglishAPIError(str(exc)) from exc
        return user.email

    def login(self, email: str, password: str) -> str:
        """Authenticate and persist the SDK session for future CLI runs."""
        try:
            user = self._auth.login(email, password, client_type="spanglish-cli")
        except (R2D2Error, httpx.HTTPError, ValidationError) as exc:
            raise SpanglishAPIError(str(exc)) from exc
        return user.email

    def register(self, username: str, email: str, password: str) -> str:
        """Create an R2D2 user account and return its email address."""
        try:
            user = self._auth.register(username, email, password)
        except (R2D2Error, httpx.HTTPError, ValidationError) as exc:
            raise SpanglishAPIError(str(exc)) from exc
        return user.email

    def request_password_reset(self, email: str) -> None:
        """Ask the API to email a password-reset token when the account exists."""
        operation = getattr(self._auth, "request_password_reset", None)
        if operation is None:
            self._public_auth_request("/password-reset/request", {"email": email})
            return
        try:
            operation(email)
        except (R2D2Error, httpx.HTTPError, ValidationError) as exc:
            raise SpanglishAPIError(str(exc)) from exc

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        """Replace a forgotten password using the emailed reset token."""
        operation = getattr(self._auth, "confirm_password_reset", None)
        if operation is None:
            self._public_auth_request(
                "/password-reset/confirm",
                {"token": token, "new_password": new_password},
            )
            self._auth.token_store.clear()
            return
        try:
            operation(token, new_password)
        except (R2D2Error, httpx.HTTPError, ValidationError) as exc:
            raise SpanglishAPIError(str(exc)) from exc

    def _public_auth_request(self, path: str, payload: dict[str, str]) -> None:
        """Call public reset endpoints when an older SDK is installed."""
        try:
            response = self._health.post(f"/api/v1/auth{path}", json=payload)
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
            raise SpanglishAPIError(f"Could not connect to the API: {exc}") from exc

    def get_quiz_options(self) -> QuizOptions:
        """Fetch languages, categories, content types, and quiz modes."""
        return QuizOptions.model_validate(self._request("GET", "/quiz-options"))

    def create_category(self, name: str) -> Reference:
        """Create a vocabulary and quiz category through the shared API."""
        return Reference.model_validate(
            self._request("POST", "/categories", json={"name": name})
        )

    def list_chapters(self) -> list[Reference]:
        """Fetch chapters available for vocabulary and quizzes."""
        return [
            Reference.model_validate(item) for item in self._request("GET", "/chapters")
        ]

    def create_chapter(self, name: str) -> Reference:
        """Create a chapter through the shared API."""
        return Reference.model_validate(
            self._request("POST", "/chapters", json={"name": name})
        )

    def list_artists(self) -> list[Reference]:
        """List artists owned by the logged-in user."""
        return [
            Reference.model_validate(item) for item in self._request("GET", "/artists")
        ]

    def create_artist(self, name: str) -> Reference:
        """Create an artist owned by the logged-in user."""
        return Reference.model_validate(
            self._request("POST", "/artists", json={"name": name})
        )

    def list_songs(self, artist_id: int) -> list[Song]:
        """List this user's songs for one artist."""
        return [
            Song.model_validate(item)
            for item in self._request("GET", "/songs", params={"artist_id": artist_id})
        ]

    def create_song(self, title: str, artist_id: int) -> Song:
        """Create a song under one of this user's artists."""
        return Song.model_validate(
            self._request(
                "POST", "/songs", json={"title": title, "artist_id": artist_id}
            )
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
            key: value for key, value in optional_params.items() if value is not None
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

    def list_quiz_results(self, limit: int = 5) -> list[QuizHistoryItem]:
        """Fetch the authenticated learner's most recent completed quiz scores."""
        return [
            QuizHistoryItem.model_validate(item)
            for item in self._request(
                "GET", "/quizzes/results", params={"limit": limit}
            )
        ]

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Send a request and translate HTTP/network errors for terminal display."""
        try:
            return self._auth.request(method, f"/spanglish{path}", **kwargs)
        except R2D2Error as exc:
            raise SpanglishAPIError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise SpanglishAPIError(
                f"Could not connect to the Spanglish API: {exc}"
            ) from exc
