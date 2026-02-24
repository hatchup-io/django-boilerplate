from django.contrib import admin

from common.admins.base import _HatchUpBaseAdmin
from common.admins.base import admin_site
from document.models import Document


@admin.register(Document, site=admin_site)
class DocumentAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "original_filename",
        "file_type",
        "user",
        "type",
        "is_active",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("file_type", "type")
    search_fields = ("original_filename", "filename", "user__email")
    readonly_fields = ("filename", "file_path", "file_size_bytes", "content_hash")
