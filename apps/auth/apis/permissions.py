from __future__ import annotations

from typing import Iterable

from rest_framework.permissions import BasePermission

from apps.auth.services.object_permissions import user_has_object_perms
from apps.auth.services.roles import has_any_role, is_platform_admin


class IsAdminRole(BasePermission):
    def has_permission(self, request, view) -> bool:
        return is_platform_admin(request.user)


class IsStartupRole(BasePermission):
    """
    Convenience wrapper (not required by the system).
    If you want fully dynamic roles, prefer `DenyIfRoleNotAllowedForEndpoint`.
    """

    def has_permission(self, request, view) -> bool:
        return has_any_role(request.user, ["Startup"])


class IsInvestorRole(BasePermission):
    """
    Convenience wrapper (not required by the system).
    If you want fully dynamic roles, prefer `DenyIfRoleNotAllowedForEndpoint`.
    """

    def has_permission(self, request, view) -> bool:
        return has_any_role(request.user, ["Investor"])


class DenyIfRoleNotAllowedForEndpoint(BasePermission):
    """
    Endpoint-level role gate to avoid "role checks everywhere".

    Usage:
    - Set `allowed_roles = [RoleName.STARTUP, RoleName.ADMIN]` on the view.
    - Admin always passes.
    """

    message = "Your role is not allowed to access this endpoint."

    def has_permission(self, request, view) -> bool:
        if is_platform_admin(request.user):
            return True

        # Support both names for backwards compatibility:
        # - `allowed_groups`: preferred (roles == group names)
        # - `allowed_roles`: legacy
        allowed = getattr(view, "allowed_groups", None) or getattr(
            view, "allowed_roles", None
        )
        if not allowed:
            # Explicit by default: if the view didn't declare its boundary, deny.
            return False

        allowed_group_names = [str(r) for r in allowed]
        return has_any_role(request.user, allowed_group_names)


class HasObjectPermission(BasePermission):
    """
    Object-level permission using internal object-permission engine.

    Usage:
    - Set `object_perms_map` (preferred) or `guardian_perms_map` (legacy) on the view,
      keyed by `view.action`.
      Example:
        object_perms_map = {"retrieve": ["users.view_user"], ...}
    """

    message = "You do not have permission to access this object."

    def has_object_permission(self, request, view, obj) -> bool:
        if is_platform_admin(request.user):
            return True

        action = getattr(view, "action", None) or ""
        perms_map = (
            getattr(view, "object_perms_map", None)
            or getattr(view, "guardian_perms_map", None)
            or {}
        )
        required = perms_map.get(action) or perms_map.get("*")
        if not required:
            # Explicit by default: if object perms aren't declared, deny.
            return False

        required_perms: Iterable[str] = required
        return user_has_object_perms(
            request=request, obj=obj, required_perms=required_perms
        )
