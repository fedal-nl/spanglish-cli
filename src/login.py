"""Store an authenticated R2D2 session for the Spanglish CLI."""

import getpass

from pydantic import ValidationError
from r2d2_sdk import FileTokenStore, R2D2Client, R2D2Error

from src.settings import API_TIMEOUT_SECONDS, R2D2_API_URL, TOKEN_STORE_PATH


def login() -> None:
    """Prompt for credentials and persist the resulting refreshable session."""
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    try:
        with R2D2Client(
            R2D2_API_URL,
            token_store=FileTokenStore(TOKEN_STORE_PATH),
            timeout=API_TIMEOUT_SECONDS,
        ) as client:
            user = client.login(email, password, client_type="spanglish-cli")
    except (ValidationError, R2D2Error) as exc:
        raise SystemExit(f"Login failed: {exc}") from exc
    print(f"Authenticated as {user.email}. Session saved to {TOKEN_STORE_PATH}.")


if __name__ == "__main__":
    login()
