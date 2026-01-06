.PHONY: start

# ---------------------------------
# Application start command
# ---------------------------------
start:
	@echo "Starting dictionary app..."
	uv run python -m src.dictionary_app

# ---------------------------------
# Alembic migration commands
# ---------------------------------
# To run migrations. first generate a new migration script:
migrate:
	uv run alembic revision --autogenerate -m "<migration_message>"
# Then apply the migration: (Optional with envfile): ENV_FILE=.env.prod uv run alembic upgrade head
upgrade:
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

# ---------------------------------
# Bump version and tag release
# ---------------------------------
patch:
	uv run bump2version patch

minor:
	uv run bump2version minor

major:
	uv run bump2version major

# Full release: bump patch, commit, tag, push
release: patch
	@git push origin HEAD      # push commit
	@git push origin --tags    # push new tag
	@echo "Release done and pushed!"

# ---------------------------------
# Clean Python cache
# ---------------------------------
clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__ *.pyc *.pyo

# ---------------------------------
# Help
# ---------------------------------
help:
	@echo "Available make commands:"
	@echo "  make start       - Run the application"
	@echo "  make test        - Run tests with pytest"
	@echo "  make migrate     - Generate Alembic migration"
	@echo "  make upgrade     - Apply Alembic migrations"
	@echo "  make release     - Bump patch version and tag release"
	@echo "  make patch       - Bump patch version"
	@echo "  make minor       - Bump minor version"
	@echo "  make major       - Bump major version"
	@echo "  make clean       - Remove Python cache files"
	@echo "  make help        - Show this help message"