# Architecture

## Layout

```
core/                       Django project (settings, urls, wsgi/asgi)
  packages/                 Per-package config (drf, drf_spectacular, simple_jwt, sentry, cors, ckeditor)
apps/
  common/                   Cross-cutting infrastructure (no domain code)
    apis/views/             HatchupBaseView, HatchupBaseViewset, HatchupModelViewset, ...
    apis/serializers/       Envelope serializers, custom fields
    configs/classes/        HatchupJWTAuthentication, DefaultPagination, HatchupAutoSchema
    configs/constants/      Shared TextChoices (workflow, type)
    models/                 HatchUpBaseModel, StateTransitionMixin, WorkflowStage/State/Transition, Type
    managers/               HatchUpBaseManager (soft-delete)
    utils/                  Exception handler, health check, storage helpers, swagger utils
    admins/                 Custom admin site, _HatchUpBaseAdmin, model admins for shared models
    exceptions.py           Domain exception hierarchy (DomainError, NotFoundError, ConflictError, ...)
    management/commands/    setup_roles, startapp
  auth/                     JWT login + OTP services (no User model)
  users/                    Custom User model + registration + profile
  notification/             Notifications + email service
  document/                 Document upload
  messaging/                Conversations + messages
  app_template/             .py-tpl scaffolding for new apps
docs/                       This directory
scripts/init_project.py     One-time project rename (template → your project)
```

## Base classes

Inherit, don't duplicate.

### Models — `HatchUpBaseModel`

Soft-deletable, auditable, ordered-by-newest. Adds `is_active`, `is_deleted`, `created_at`, `updated_at`. The default manager is `HatchUpBaseManager`, which filters `is_active=True, is_deleted=False`. Use `Model.objects.delete()` for soft delete; `.purge()` for hard delete.

### Views — `HatchupAPIView`, `HatchupModelViewset`, ...

All API responses go through `_EnvelopeFinalizeMixin.finalize_response`, which wraps them as `{ message, status, pagination, data }`. Error responses (4xx/5xx) surface their `detail` or first field error as the envelope `message`. Streaming/binary responses pass through.

Available variants:
- `HatchupAPIView` — single-action endpoint (login, register).
- `HatchupBaseViewset` — base for ViewSets (no CRUD mixed in).
- `HatchupReadViewset` — list + retrieve.
- `HatchupUpsertViewset` — create + update + destroy.
- `HatchupModelViewset` — full CRUD.

### Admin — `_HatchUpBaseAdmin`, `admin_site`

Use `apps.common.admins.admin_site` instead of Django's default `admin.site`. Inherit from `_HatchUpBaseAdmin` for soft-delete-aware admin behavior.

## Response envelope

All API JSON responses look like:

```json
{
  "message": "Request was successful",
  "status": 200,
  "pagination": null,
  "data": { ... }
}
```

For paginated list responses, `pagination` is populated:

```json
{
  "message": "Request was successful",
  "status": 200,
  "pagination": {
    "links": { "next": "...", "previous": null },
    "total_pages": 3,
    "current_page": 1,
    "total_items": 25
  },
  "data": [ ... ]
}
```

Errors:

```json
{
  "message": "This email cannot be used for registration.",
  "status": 400,
  "pagination": null,
  "data": { "email": ["This email cannot be used for registration."] }
}
```

`HatchupAutoSchema` (drf-spectacular) wraps response schemas to match this shape, so Swagger documentation is accurate.

## Domain exceptions

Services raise `apps.common.exceptions.{DomainError, NotFoundError, ConflictError, BusinessRuleError, PermissionDeniedError}`. The DRF exception handler maps them to HTTP responses. Views and serializers stay free of HTTP concerns.

```python
from apps.common.exceptions import ConflictError

def create_user(*, email: str, password: str) -> User:
    if User.objects.filter(email=email).exists():
        raise ConflictError("Email already in use.")
    ...
```

## Soft delete

`HatchUpBaseManager.delete()` flips `is_deleted=True` (preserving the row); `.purge()` runs the underlying SQL DELETE. Default queries hide soft-deleted rows. To see everything (e.g., admin), use `Model.all_objects` if exposed (otherwise call `.purge()` carefully).

## State machines (optional)

`StateTransitionMixin` (in `apps/common/models/common_workflow_models.py`) integrates with `django-fsm-2`. Models declare a `state` field and decorate transition methods; the mixin records every transition into `StateTransitionLog`.

## Async tasks

The template ships **no task queue**. The `EmailService` uses synchronous `send_mail`. Production projects should pick a queue (Celery, RQ, dramatiq, django-q) and replace the synchronous call.
