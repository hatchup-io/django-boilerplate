from django.contrib import admin

from apps.common.admins.base import _HatchUpBaseAdmin, admin_site
from apps.notification.models.notification_models import (
    Notification,
    NotificationRoleTarget,
    NotificationUser,
)


@admin.register(Notification, site=admin_site)
class NotificationAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "is_global",
        "expires_at",
        "created_at",
        "is_active",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("category", "is_global")
    search_fields = ("title", "message", "category")
    date_hierarchy = "created_at"


@admin.register(NotificationUser, site=admin_site)
class NotificationUserAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "notification",
        "user",
        "read_at",
        "archived_at",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("read_at", "archived_at")
    search_fields = ("notification__title", "user__email")
    autocomplete_fields = ("notification", "user")
    list_select_related = ("notification", "user")


@admin.register(NotificationRoleTarget, site=admin_site)
class NotificationRoleTargetAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "notification", "role", "created_at", "is_active")
    list_filter = _HatchUpBaseAdmin.list_filter + ("role",)
    search_fields = ("notification__title", "role__name")
    autocomplete_fields = ("notification", "role")
    list_select_related = ("notification", "role")
