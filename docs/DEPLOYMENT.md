# Deployment

## Environment variables

Copy `.env.example` to `.env` and fill in:

| Variable | Purpose |
|---|---|
| `DEBUG` | `True` for dev, `False` for prod. |
| `SECRET_KEY` | Django secret. **Set a real value in prod** — the default in `core/settings.py` is for development only. |
| `ALLOWED_HOSTS` | Comma-separated host list. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins for unsafe requests. |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | Postgres connection. |
| `TEST_DB_*` | Optional override for pytest. |
| `REDIS_URL` | Optional. If unset, the cache falls back to `LocMemCache`. |
| `RUSTFS_*` / S3 credentials | Optional. If unset, media is stored on the local filesystem. |
| `SENTRY_DSN` | Optional. Leave empty to disable Sentry. |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.0` – `1.0`, default `0.1`. |
| `EMAIL_BACKEND` | Django email backend dotted path. Defaults to console in dev. |
| `DEFAULT_FROM_EMAIL` | Sender used by `EmailService`. |

## Local development (Docker)

```
cp .env.example .env
docker compose up --build
```

The default `docker-compose.yml` provides Postgres (`db`), Redis (`redis`), and RustFS (`rustfs`). The web service uses `Dockerfile` by default; for a dev image with editor tooling and dev deps, swap to `Dockerfile.local`.

## Local development (no Docker)

```
uv sync --dev
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py setup_roles      # optional: create base role groups
uv run python manage.py runserver
```

## Tests

```
uv run pytest
```

Requires a Postgres instance reachable via the `DB_*` (or `TEST_DB_*`) env vars. CI uses a `postgres:16-alpine` service; locally, either run the docker-compose `db` service or use a host Postgres.

## Production notes

- `Dockerfile` builds a slim image with no dev deps. Replace `runserver` (currently the `CMD`) with a real WSGI/ASGI server in your deployment manifest:
    - `gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers <N>`
- Set `DEBUG=False`, a real `SECRET_KEY`, and a real `ALLOWED_HOSTS`.
- Run migrations + collectstatic at deploy time (already wired into `entrypoint.sh`).
- The template ships **no task queue**. If you need async work (email, webhooks, periodic jobs), add Celery, RQ, dramatiq, or django-q at deploy time. `EmailService.send_otp_email` calls `send_mail` synchronously — replace that call with a queued equivalent.
- `HatchUpBaseManager` filters soft-deleted rows by default. Audit any cron / management command that needs to see all rows.
