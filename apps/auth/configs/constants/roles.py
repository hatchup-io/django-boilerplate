from __future__ import annotations

from enum import Enum


class RoleName(str, Enum):
    """
    Role names are stored in Django `Group.name`.

    We use Django Groups (rather than a custom Role model) because:
    - It integrates directly with Django's *default* permission system.
    - Admin UI + `user.groups` are first-class.
    - It's easy to extend (just add another Group + mapping in one place).

    This avoids duplicating role tables (this repo already has `users.Role`,
    but RBAC here is intentionally centralized in this app).
    """

    ADMIN = "Admin"
    STARTUP = "Startup"
    INVESTOR = "Investor"
