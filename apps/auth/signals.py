from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_migrate
from django.dispatch import receiver

from apps.auth.services.roles import (
    RoleBootstrapSpec,
    ensure_roles_exist,
    invalidate_user_roles_cache,
)

User = get_user_model()


@receiver(post_migrate)
def bootstrap_roles(sender, **kwargs) -> None:
    """
    Create role groups + attach model-level permissions after migrations.

    This keeps role setup deterministic across environments (dev/staging/prod)
    and avoids "manual group setup" steps.
    """

    # Only run after migrating *this* app (label is unique even though module is `auth`).
    if sender.label != "authz":
        return

    # Role bootstrapping is dynamic:
    # - Define any number of roles/groups in settings.AUTHZ_ROLE_DEFINITIONS.
    # - No code changes needed to add a new role.
    #
    # Format:
    #   AUTHZ_ROLE_DEFINITIONS = {
    #     "Admin": {"users": ["view_user", "change_user"]},
    #     "Member": {"users": ["view_user"]},
    #     ...
    #   }
    role_defs: dict = getattr(settings, "AUTHZ_ROLE_DEFINITIONS", {})
    specs: list[RoleBootstrapSpec] = []
    for group_name, app_perms in role_defs.items():
        for app_label, codenames in (app_perms or {}).items():
            specs.append(
                RoleBootstrapSpec(
                    group_name=str(group_name),
                    permission_codenames=tuple(str(c) for c in (codenames or [])),
                    permission_app_label=str(app_label),
                )
            )
    if specs:
        ensure_roles_exist(specs=specs)


@receiver(m2m_changed, sender=User.groups.through)
def invalidate_roles_cache_on_group_change(sender, instance: User, **kwargs) -> None:
    # Keep `auth.services.roles.get_user_roles()` cache fresh when roles change.
    invalidate_user_roles_cache(instance.id)
