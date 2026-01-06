.PHONY: start

start:
	@echo "Starting dictionary app..."
	uv run python -m src.dictionary_app

# To run migrations. first generate a new migration script:
migrations:
	uv run alembic revision --autogenerate -m "<migration_message>"
# Then apply the migration: (Optional with envfile): ENV_FILE=.env.prod uv run alembic upgrade head
migrate:
	uv run alembic upgrade head
# To downgrade to a previous migration:
downgrade:
	uv run alembic downgrade <revision_id>
# To view current revision:
current:
	uv run alembic current
# To view the history of migrations:
history:
	uv run alembic history --verbose
# To stamp the database with a specific revision without running migrations:
stamp:
	uv run alembic stamp <revision_id>
