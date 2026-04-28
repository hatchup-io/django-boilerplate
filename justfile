default:
    @just --list

# --- Code quality ---
# Format all files
fmt:
    uv run ruff format .

# Fix linting issues
lint-fix:
    uv run ruff check . --fix

# Format and lint-fix
fix: fmt lint-fix

# Verify formatting and lint (no changes)
check:
    uv run ruff format --check .
    uv run ruff check .

# Run mypy
typecheck:
    uv run mypy apps core

# Run pre-commit on all files
pre-commit:
    uv run pre-commit run --all-files

# Format, lint-fix, and verify
all: fmt lint-fix check typecheck

# --- Tests ---
# Run pytest
test *ARGS:
    uv run pytest {{ARGS}}

# --- Local run ---
# Run dev server (no Docker)
run:
    uv run python manage.py runserver

# Apply migrations locally
migrate:
    uv run python manage.py migrate
