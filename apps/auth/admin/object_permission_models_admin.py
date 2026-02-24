from django.contrib import admin

from apps.auth.models.object_permission_models import UserObjectPermission
from apps.common.admins.base import _HatchUpBaseAdmin, admin_site


@admin.register(UserObjectPermission, site=admin_site)
class UserObjectPermissionAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "user", "perm_codename", "content_type", "object_id")
    list_filter = ("content_type",)
    search_fields = ("perm_codename", "object_id", "user__email")
    raw_id_fields = ("user", "content_type")
    ordering = ("-id",)
