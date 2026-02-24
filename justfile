default:
    @just --list

# --- Code quality ---
# Format all files
fmt:
    ruff format .

# Fix linting issues
lint-fix:
    ruff check . --fix

# Format and lint-fix
fix: fmt lint-fix

# Verify formatting and lint (no changes)
check:
    ruff format --check .
    ruff check .

# Format, lint-fix, and verify
all: fmt lint-fix check

# --- Local run ---
# Run dev server (no Docker)
run:
    uv run python manage.py runserver

# Apply migrations locally
migrate:
    uv run python manage.py migrate
