# Spanglish CLI

Spanglish CLI is an interactive terminal client for the versioned Spanglish
FastAPI service. Vocabulary, conjugations, quiz definitions, attempts, scores,
and advice are stored and calculated by the backend rather than a local database.

## Architecture

```text
Interactive prompts -> typed Pydantic models -> HTTP client
                    -> /api/v1/spanglish -> PostgreSQL
```

The CLI runs a fetched quiz locally and sends all answers to the backend once it
is complete. Accepted answers are included in the quiz response, allowing the
terminal to show immediate feedback, but the API recalculates the authoritative
score.

## Requirements

- Python 3.14
- `uv`
- The R2D2 FastAPI backend running with its database migrations applied

Install dependencies:

```bash
uv sync
```

## Configuration

Copy the provided configuration template and adjust the API URL:

```bash
cp .env.example .env
```

The available variables are:

```dotenv
SPANGLISH_API_URL=http://127.0.0.1:8000/api/v1/spanglish
API_TIMEOUT_SECONDS=15
R2D2_TOKEN_STORE_PATH=~/.config/spanglish/tokens.json
```

Start the backend separately, then verify it at:

```text
http://127.0.0.1:8000/health
```

Create an API account once before using authenticated quiz operations:

```bash
make create-account
```

The command prompts for a username, email, password, and password confirmation,
then registers the account through `r2d2-sdk-auth`. It uses the API root derived
from `SPANGLISH_API_URL`.

Log in once to save a refreshable authentication session:

```bash
make login
```

On every startup, the CLI checks the API connection and then validates the
saved session. The SDK refreshes expired access tokens automatically. If no
valid session is available, the CLI prompts for email and password, saves the
new session, and continues to the menu. New users can select **Sign up** instead;
the CLI creates their account and logs them in immediately. A connection,
registration, or login failure prints the error and stops before showing the
menu.

The authentication menu also provides **Forgot password**. It requests a reset
token by email, accepts the token and a new password, and logs the user in after
the reset succeeds. The reset flow remains compatible with SDK releases that
predate the password-reset convenience methods.

## Run

```bash
uv run python -m src.dictionary_app
```

The menu supports:

- Create chapters for lesson-based vocabulary and quizzes.
- Create categories used to organize vocabulary and quizzes.
- Create vocabulary, translations, and present-tense verb conjugations.
- Reuse category, vocabulary type, and chapter selections when entering several
  vocabulary items in one batch.
- Automatically use the `Phrase` vocabulary type when the `Phrases` category is
  selected, skipping the redundant vocabulary-type menu.
- Answer confirmation questions with selectable Yes/No choices instead of typed
  letters; every confirmation also includes the global red Quit entry.
- Optionally assign vocabulary to a chapter or leave it without one.
- Read and filter vocabulary by category.
- Update a complete vocabulary card.
- Delete vocabulary after confirmation.
- Configure and complete Spanish/English translation and conjugation quizzes.
- Run quizzes across all chapters or filter them to one chapter.
- Submit quiz attempts and display the API score and advice.
- Quit explicitly from every selection menu. The global Quit entry is red so it
  is visually separate from API data and normal actions. Terminal interrupts
  also exit cleanly without printing a traceback.

## API operations used

| CLI operation | API operation |
| --- | --- |
| Load menus | `GET /api/v1/spanglish/quiz-options` |
| List/create chapters | `GET/POST /api/v1/spanglish/chapters` |
| Create categories | `POST /api/v1/spanglish/categories` |
| List vocabulary | `GET /api/v1/spanglish/vocabulary` |
| Read vocabulary | `GET /api/v1/spanglish/vocabulary/{id}` |
| Create vocabulary | `POST /api/v1/spanglish/vocabulary` |
| Update vocabulary | `PUT /api/v1/spanglish/vocabulary/{id}` |
| Delete vocabulary | `DELETE /api/v1/spanglish/vocabulary/{id}` |
| Generate quiz | `POST /api/v1/spanglish/quizzes` |
| Submit results | `POST /api/v1/spanglish/quizzes/{id}/results` |

## Tests

Tests use `httpx.MockTransport`; they do not require a running API or database.

```bash
uv run pytest
```

## Local database retirement

Alembic, SQLAlchemy, PostgreSQL drivers, migration files, and the old `src/db`
package were removed. Pydantic remains the boundary-validation library for API
responses and locally collected quiz attempts.

The historical `spanish.db` file is intentionally retained as a backup. It is
not opened or modified by the CLI. Its contents can later be imported into the
FastAPI backend with a one-time migration script.
