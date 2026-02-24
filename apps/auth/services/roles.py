from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth.models import Group, Permission
from django.core.cache import cache

ROLE_CACHE_TTL_SECONDS = 60


@dataclass(frozen=True)
class RoleBootstrapSpec:
    """
    Bootstrap spec for a Django Group.

    Roles are dynamic: any Group name is a role.
    We keep a small bootstrap hook for "default roles", but the RBAC layer itself
    does not require a fixed set of roles.
    """

    group_name: str
    # Model-level permissions (RBAC) this role should have.
    # Object-level permissions are enforced via guardian and handled separately.
    permission_codenames: tuple[str, ...] = ()
    # Optional: constrain permissions to a specific app_label to avoid codename collisions.
    permission_app_label: str | None = None


def ensure_roles_exist(specs: Iterable[RoleBootstrapSpec]) -> dict[str, Group]:
    """
    Create groups for each role and attach model-level permissions.

    Why model perms?
    - DRF endpoints usually need coarse "can access this resource type" gates.
    - Object-level checks (guardian) then restrict which objects within the type.
    """

    groups: dict[str, Group] = {}
    for spec in specs:
        group, _ = Group.objects.get_or_create(name=spec.group_name)
        if spec.permission_codenames:
            perms = Permission.objects.filter(codename__in=spec.permission_codenames)
            if spec.permission_app_label:
                perms = perms.filter(content_type__app_label=spec.permission_app_label)
            group.permissions.set(perms)
        groups[spec.group_name] = group
    return groups


def _role_cache_key(user_id: int) -> str:
    return f"auth.roles.v1.user:{user_id}"


def get_user_roles(user) -> set[str]:
    """
    Return roles as a set[str] of Django Group names.

    Performance:
    - Uses caching because this is frequently called by DRF permission classes.
    - Cache TTL is short to avoid stale authZ; invalidate by deleting the key when
      changing user.groups in admin or via service calls.
    """

    if not getattr(user, "is_authenticated", False):
        return set()

    key = _role_cache_key(user.id)
    cached = cache.get(key)
    if cached is not None:
        return set(cached)

    role_names = set(user.groups.values_list("name", flat=True))
    cache.set(key, list(role_names), timeout=ROLE_CACHE_TTL_SECONDS)
    return role_names


def invalidate_user_roles_cache(user_id: int) -> None:
    cache.delete(_role_cache_key(user_id))


def is_platform_admin(user) -> bool:
    """
    Platform admin bypass.

    We treat Django superusers as "admin" regardless of group membership.
    If you want a group-driven admin role instead, use `DenyIfRoleNotAllowedForEndpoint`
    with an allowed group like "Admin".
    """

    return bool(getattr(user, "is_superuser", False))


def has_any_role(user, allowed_roles: Iterable[str]) -> bool:
    """
    Role check against arbitrary group names.
    """

    if is_platform_admin(user):
        return True
    roles = get_user_roles(user)
    return bool(roles.intersection(set(allowed_roles)))
