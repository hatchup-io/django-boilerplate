from django.contrib import admin

from common.admins.base import _HatchUpBaseAdmin
from common.admins.base import admin_site
from users.models.users_role_models import UserRole
from users.models.users_user_models import User


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0
    autocomplete_fields = ("role",)


@admin.register(User, site=admin_site)
class UserAdmin(_HatchUpBaseAdmin):
    inlines = [UserRoleInline]
    list_display = (
        "id",
        "email",
        "full_name",
        "phone_number",
        "is_superuser",
        "is_active",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("is_superuser",)
    search_fields = (
        "email",
        "phone_number",
        "first_name",
        "last_name",
    )
    date_hierarchy = "created_at"
