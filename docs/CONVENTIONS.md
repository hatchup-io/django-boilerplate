# Conventions

The canonical short list lives in [`.cursorrules`](../.cursorrules). This file expands on it with rationale.

## Per-app layout

Every app under `apps/` follows:

```
apps/<app>/
  apis/
    serializers/                 Per-entity, prefixed: <entity>_serializers.py
    views/                       Per-entity, prefixed: <entity>_views.py or <entity>_viewsets.py
    urls.py                      Router + extra paths; mounted in core/urls.py at /api/<app>/
  configs/
    constants/<app>_*_enums.py   TextChoices/IntegerChoices live here, not in models
  models/<app>_<entity>_models.py
  services/                      Module-level functions; non-trivial business logic lives here
  admin/<entity>_admin.py        @admin.register(Model, site=admin_site) on _HatchUpBaseAdmin subclass
  managers/                      Custom managers/querysets when needed
  tests/                         pytest tests; per-entity files
  signals.py                     Django signals (only when needed)
  apps.py                        AppConfig
```

The `apps/app_template/` directory is the canonical scaffold — copy it for new apps and replace `{{ app_name }}`, `{{ entity }}`, `{{ Entity }}`, `{{ Tag }}` placeholders.

## Where logic goes

| Concern | Place it in |
|---|---|
| Field-shape validation | Serializer (`validators=[...]`, `validate_<field>`) |
| Business rule validation | Service (raise `BusinessRuleError` or `ConflictError`) |
| Persistence (`Model.objects.create/update/...`) | Service |
| HTTP handling | View / ViewSet |
| Cross-cutting reads (search, filtering) | `_SearchableQuerysetMixin` + `DjangoFilterBackend` |
| Async work | (Pick a queue when you need it — template ships none.) |

Keep views thin: validate → call service → return service's result. Keep serializers free of `Model.objects.*` calls — they're DTOs, not orchestrators.

## Naming

- Apps: snake_case (`users`, `auth`, `notification`).
- Model files: `<app>_<entity>_models.py` (`users_user_models.py`, `messaging_models.py`).
- Service files: module-level functions (`create_user_services.py`, `otp_service.py`). Avoid static-method classes — pick functions.
- Models: PascalCase (`User`, `Conversation`).
- Constants/enums: `<app>_<feature>_enums.py` exposing `TextChoices` / `IntegerChoices`.
- Tests: `test_<thing>.py` under `tests/`.

## Imports

- One import per line (matches `force-single-line = true` in `[tool.ruff.lint.isort]`).
- Stdlib → third-party → local; ruff/isort enforce this.
- All imports at the top of the file; no inline imports except to break a real circular dependency.

## Quotes & formatting

- Double quotes everywhere (ruff format default).
- Line length 120.
- `from __future__ import annotations` at the top of new modules.

## OpenAPI

- Every endpoint gets `@extend_schema` (or `@extend_schema_view` for ViewSets). Use `tags=[...]` consistently per app.
- `HatchupAutoSchema` wraps 2xx response schemas in the envelope automatically; don't hand-roll envelope serializers in `responses=`.

## Pre-commit

Run once per checkout:

```
uv run pre-commit install
```

Ruff (check + format) and isort run on every commit. CI re-runs `pre-commit run --all-files`.

## Tests

- pytest, not Django `TestCase`. Use `@pytest.mark.django_db` (or `pytestmark = pytest.mark.django_db`).
- Factories live in `apps/<app>/tests/factories.py`. Use `factory_boy` (installed as a dev dep).
- Top-level `conftest.py` exposes `api_client`, `user`, `auth_client`. Per-app conftest files add domain fixtures.
- See `apps/users/tests/test_users_authentication.py` for an example.

## Type checking

`mypy apps core` runs against the codebase. `django-stubs` and `djangorestframework-stubs` provide type info. Strict-by-default settings; migrations are excluded.
