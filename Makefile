.PHONY: start create-account login test lint patch minor major release clean help

# ---------------------------------
# Application start command
# ---------------------------------
start:
	@echo "Starting dictionary app..."
	uv run python -m src.dictionary_app

create-account:
	@uv run python -m src.create_account

login:
	@uv run python -m src.login

# ---------------------------------
# Quality checks
# ---------------------------------
test:
	uv run pytest

lint:
	uv run ruff check .

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
	@echo "  make create-account - Create an R2D2 API user account"
	@echo "  make login       - Log in and save the CLI authentication session"
	@echo "  make test        - Run tests with pytest"
	@echo "  make lint        - Run Ruff"
	@echo "  make release     - Bump patch version and tag release"
	@echo "  make patch       - Bump patch version"
	@echo "  make minor       - Bump minor version"
	@echo "  make major       - Bump major version"
	@echo "  make clean       - Remove Python cache files"
	@echo "  make help        - Show this help message"
