"""Interactive account registration for the Spanglish CLI."""

import getpass

from pydantic import ValidationError
from r2d2_sdk import R2D2Client, R2D2Error

from src.settings import R2D2_API_URL


def api_root(spanglish_url: str = R2D2_API_URL) -> str:
    """Return the R2D2 API root from the configured Spanglish endpoint."""
    return spanglish_url


def create_account() -> None:
    """Prompt for registration fields and create an account through the SDK."""
    print(f"Create an account at {api_root()}")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    try:
        with R2D2Client(api_root()) as client:
            user = client.register(username, email, password)
    except ValidationError as exc:
        raise SystemExit(f"Invalid account details: {exc}") from exc
    except R2D2Error as exc:
        raise SystemExit(f"Could not create account: {exc}") from exc

    print(f"Account created for {user.email}. You can now log in.")


if __name__ == "__main__":
    create_account()
