from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group as AuthGroup


class _HatchUpBaseAdmin(admin.ModelAdmin):
    """
    Shared admin defaults for HatchUpBaseModel-based models.

    Import and subclass this in per-model admin modules.
    """

    list_filter = ("is_active", "is_deleted", "created_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


class HatchupAdminSite(AdminSite):
    site_header = "Hatchup Admin"
    site_title = "Hatchup Admin Portal"
    index_title = "Welcome to Hatchup"


admin_site = HatchupAdminSite(name="hatchup_admin")

# Register Group so autocomplete_fields on UserRoleInline and others work.
class GroupAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


admin_site.register(AuthGroup, GroupAdmin)
