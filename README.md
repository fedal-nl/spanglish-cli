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

## Run

```bash
uv run python -m src.dictionary_app
```

The menu supports:

- Create chapters for lesson-based vocabulary and quizzes.
- Create vocabulary, translations, and present-tense verb conjugations.
- Optionally assign vocabulary to a chapter or leave it without one.
- Read and filter vocabulary by category.
- Update a complete vocabulary card.
- Delete vocabulary after confirmation.
- Configure and complete Spanish/English translation and conjugation quizzes.
- Run quizzes across all chapters or filter them to one chapter.
- Submit quiz attempts and display the API score and advice.

## API operations used

| CLI operation | API operation |
| --- | --- |
| Load menus | `GET /api/v1/spanglish/quiz-options` |
| List/create chapters | `GET/POST /api/v1/spanglish/chapters` |
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
