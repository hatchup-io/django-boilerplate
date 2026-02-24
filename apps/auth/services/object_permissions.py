from __future__ import annotations

from typing import Iterable, Type

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Model, QuerySet

from apps.auth.services.roles import is_platform_admin
from apps.auth.models.object_permission_models import UserObjectPermission

User = get_user_model()


def _model_perm(app_label: str, codename: str) -> str:
    return f"{app_label}.{codename}"


def default_object_perms_for_model(model: Type[Model]) -> tuple[str, str, str]:
    """
    Default object-level permissions we assign to owners.

    Why no "add"?
    - "add" is not object-scoped; it's checked at the model level.
    """

    meta = model._meta
    return (
        _model_perm(meta.app_label, f"view_{meta.model_name}"),
        _model_perm(meta.app_label, f"change_{meta.model_name}"),
        _model_perm(meta.app_label, f"delete_{meta.model_name}"),
    )


def assign_owner_object_perms(*, user: User, obj: Model) -> None:
    """
    Assign object-level perms to the owning user.

    Performance:
    - Writes to our internal object-permission table.
    - Done on creation (signals) to keep read-path checks efficient.
    """

    ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    perms = default_object_perms_for_model(type(obj))
    rows = [
        UserObjectPermission(
            user=user,
            content_type=ct,
            object_id=obj.pk,
            perm_codename=perm,
        )
        for perm in perms
    ]
    # Ignore duplicates if called twice.
    UserObjectPermission.objects.bulk_create(rows, ignore_conflicts=True)


def filter_queryset_by_object_perm(
    *,
    user: User,
    queryset: QuerySet,
    perm: str,
) -> QuerySet:
    """
    Efficient LIST filtering using guardian.

    Critical performance strategy:
    - We **do not** call `has_perm(obj)` per row (would cause N+1 queries).
    - We use `get_objects_for_user`, which returns a queryset constrained by a JOIN.
    """

    if not getattr(user, "is_authenticated", False):
        return queryset.none()
    if is_platform_admin(user):
        return queryset

    model = queryset.model
    ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
    allowed_ids = UserObjectPermission.objects.filter(
        user=user, content_type=ct, perm_codename=perm
    ).values_list("object_id", flat=True)
    # Single SQL query with a subquery; avoids N+1 checks.
    return queryset.filter(pk__in=allowed_ids)


def _request_perm_cache(request) -> dict:
    """
    Request-scoped permission cache.

    Performance:
    - We cache (content_type_id, object_id) -> set(perms) on the request.
    - This prevents repeated DB hits in a single request when multiple checks happen.
    """

    cache_obj = getattr(request, "_objperm_cache", None)
    if cache_obj is None:
        cache_obj = {}
        request._objperm_cache = cache_obj
    return cache_obj


def _get_cached_object_perms(*, request, obj: Model) -> set[str]:
    ct = ContentType.objects.get_for_model(obj, for_concrete_model=False)
    key = (ct.pk, int(obj.pk))
    cache_obj = _request_perm_cache(request)
    cached = cache_obj.get(key)
    if cached is not None:
        return cached

    perms = set(
        UserObjectPermission.objects.filter(
            user=request.user,
            content_type=ct,
            object_id=obj.pk,
        ).values_list("perm_codename", flat=True)
    )
    cache_obj[key] = perms
    return perms


def user_has_object_perms(
    *,
    request,
    obj: Model,
    required_perms: Iterable[str],
) -> bool:
    if is_platform_admin(request.user):
        return True

    perms = _get_cached_object_perms(request=request, obj=obj)
    return all(perm in perms for perm in required_perms)
