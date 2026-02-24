from django.contrib import admin

from apps.common.admins.base import _HatchUpBaseAdmin
from apps.common.admins.base import admin_site
from apps.common.models.common_type_models import Type


@admin.register(Type, site=admin_site)
class TypeAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "title", "scope", "is_active", "created_at")
    list_filter = (*_HatchUpBaseAdmin.list_filter, "scope")
    search_fields = ("title",)
