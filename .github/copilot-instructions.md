# Spanglish CLI - AI Coding Agent Instructions

## Project Overview
A Spanish-English vocabulary learning CLI built with Typer, SQLAlchemy, and Alembic. Users add words/verbs with translations and quiz themselves interactively.

## Architecture

### Database Layer (`src/db/`)
- **SQLAlchemy ORM** with declarative base in `base.py`
- **Session management**: Use `get_session()` context manager from `base.py` - never create sessions directly
- **Models** (`models.py`): `Word` (main entity) → `Translation` (1:many), `Verb` (1:1), `Quiz` (1:many)
- **CRUD** (`crud.py`): All database operations go here. Always use `selectinload()` for relationships to avoid N+1 queries
- **Database URL**: Configured in `settings.py` (defaults to SQLite, supports PostgreSQL)

### CLI Commands (`src/main.py`)
- Built with Typer for CLI framework + Questionary for interactive prompts + Rich for formatted output
- Pattern: Commands handle user interaction → call CRUD functions → display results with Rich tables
- **Capitalization convention**: Spanish words capitalized, translations lowercase (see `add_word`)

### Enums (`src/enums.py`)
- `CategoryEnum`: Defines word categories (Noun, Verb, Adjective, Days, Months, Food, Colors)
- String enum used directly in SQLAlchemy model

## Key Patterns

### Adding Database Models
1. Define model in `models.py` inheriting from `Base`
2. Import in `alembic/env.py` (required for migrations)
3. Add CRUD functions in `crud.py` using `get_session()` context manager
4. Generate migration: `alembic revision --autogenerate -m "description"`
5. Apply: `alembic upgrade head`

### CRUD Function Pattern
```python
def operation_name(...):
    with get_session() as session:
        # Use selectinload for relationships
        query = session.query(Model).options(selectinload(Model.relation))
        # ... logic
        session.commit()
        return result
```

### CLI Command Pattern
```python
@app.command()
def command_name():
    # 1. Use questionary.select() for enums
    # 2. Use typer.prompt() for text input
    # 3. Call CRUD operations
    # 4. Display with Rich tables (console.print)
```

## Development Workflow

### Running the CLI
```bash
python -m src.main [command]
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Dependencies
- Requires Python >=3.14
- Install: `pip install -e .` (from pyproject.toml)
- Core: SQLAlchemy, Alembic, Typer, Questionary, Rich, Psycopg

## Important Notes
- **Relationships**: Always use cascade="all, delete-orphan" for dependent entities (see `Word.translations`)
- **Unique constraints**: Use `__table_args__` for composite uniqueness (see `Translation`)
- **Verb conjugations**: Stored as separate columns (yo, tu, ella_el, nosotros, vosotros, ellos_ellas)
- **Quiz feature**: Currently on `feature/create-quiz` branch - tracks word quiz attempts with timestamp and correctness
