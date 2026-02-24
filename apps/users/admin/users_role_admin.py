from django.contrib import admin

from apps.users.models.users_role_models import UserRole

from apps.common.admins.base import _HatchUpBaseAdmin, admin_site
from django.contrib.auth.admin import GroupAdmin, Group


@admin.register(Group, site=admin_site)
class GroupAdmin(GroupAdmin):
    pass


@admin.register(UserRole, site=admin_site)
class UserRoleAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "user", "role", "created_at", "is_active")
    list_filter = _HatchUpBaseAdmin.list_filter + ("role",)
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "role__name",
    )
    autocomplete_fields = ("user", "role")
    list_select_related = ("user", "role")
    date_hierarchy = "created_at"
