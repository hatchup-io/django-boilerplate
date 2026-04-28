"""
Django admin registrations for the `notification` app.

Registrations are split across modules and imported here so Django admin
autodiscovery loads them.
"""

from .notification_models_admin import NotificationAdmin
from .notification_models_admin import NotificationRoleTargetAdmin
from .notification_models_admin import NotificationUserAdmin

__all__ = [
    "NotificationAdmin",
    "NotificationRoleTargetAdmin",
    "NotificationUserAdmin",
]
