"""
Django admin registrations for the `notification` app.

Registrations are split across modules and imported here so Django admin
autodiscovery loads them.
"""

from .notification_models_admin import (
    NotificationAdmin,
    NotificationRoleTargetAdmin,
    NotificationUserAdmin,
)

__all__ = [
    "NotificationAdmin",
    "NotificationRoleTargetAdmin",
    "NotificationUserAdmin",
]
