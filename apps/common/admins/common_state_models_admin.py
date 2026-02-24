from apps.common.admins.base import _HatchUpBaseAdmin, admin_site
from apps.common.models.common_workflow_models import StateTransitionLog
from django.contrib import admin


@admin.register(StateTransitionLog, site=admin_site)
class StateTransitionLogAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "content_type",
        "object_id",
        "from_state",
        "to_state",
        "transition",
        "actor",
        "is_active",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + (
        "content_type",
        "from_state",
        "to_state",
    )
    search_fields = ("object_id", "transition", "actor__email")
    date_hierarchy = "created_at"
