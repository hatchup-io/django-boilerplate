from django.contrib import admin

from apps.common.admins.base import _HatchUpBaseAdmin, admin_site
from apps.common.models.common_workflow_models import (
    WorkflowStage,
    WorkflowState,
    WorkflowTransition,
)


@admin.register(WorkflowStage, site=admin_site)
class WorkflowStageAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "scope", "code", "name", "is_active", "created_at")
    list_filter = _HatchUpBaseAdmin.list_filter + ("scope",)
    search_fields = ("scope", "code", "name")


@admin.register(WorkflowState, site=admin_site)
class WorkflowStateAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "scope",
        "code",
        "name",
        "stage",
        "is_active",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("scope", "stage")
    search_fields = ("scope", "code", "name", "stage__code")
    autocomplete_fields = ("stage",)


@admin.register(WorkflowTransition, site=admin_site)
class WorkflowTransitionAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "code",
        "name",
        "from_state",
        "to_state",
        "action",
        "requires_admin",
        "is_active",
        "created_at",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + (
        "action",
        "requires_admin",
        "from_state__scope",
        "from_state__stage",
    )
    search_fields = ("code", "name", "from_state__code", "to_state__code")
    autocomplete_fields = ("from_state", "to_state")
