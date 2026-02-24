from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.auth.services.roles import has_any_role, is_platform_admin


class NotificationEndpointPermission(BasePermission):
    """
    Allow any authenticated user for read/self actions (list, retrieve, unread_count,
    mark_read, mark_all_read). Require Admin role for create, update, destroy.
    """

    READ_ACTIONS = {"list", "retrieve", "unread_count", "mark_read", "mark_all_read"}
    message = "Your role is not allowed to access this endpoint."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        action = getattr(view, "action", None)
        if action in self.READ_ACTIONS:
            return True
        return is_platform_admin(request.user) or has_any_role(request.user, ["Admin"])
