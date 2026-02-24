from django.contrib import admin

from apps.common.admins.base import _HatchUpBaseAdmin, admin_site
from apps.messaging.models.messaging_models import (
    Conversation,
    ConversationParticipant,
    Message,
)


@admin.register(Conversation, site=admin_site)
class ConversationAdmin(_HatchUpBaseAdmin):
    list_display = (
        "id",
        "created_by",
        "last_message_at",
        "created_at",
        "is_active",
    )
    list_filter = _HatchUpBaseAdmin.list_filter + ("last_message_at",)
    search_fields = ("id", "created_by__email")
    autocomplete_fields = ("created_by",)


@admin.register(ConversationParticipant, site=admin_site)
class ConversationParticipantAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "conversation", "user", "created_at", "is_active")
    list_filter = _HatchUpBaseAdmin.list_filter
    search_fields = ("conversation__id", "user__email")
    autocomplete_fields = ("conversation", "user")
    list_select_related = ("conversation", "user")


@admin.register(Message, site=admin_site)
class MessageAdmin(_HatchUpBaseAdmin):
    list_display = ("id", "conversation", "sender", "created_at", "is_active")
    list_filter = _HatchUpBaseAdmin.list_filter
    search_fields = ("content", "sender__email")
    autocomplete_fields = ("conversation", "sender")
    list_select_related = ("conversation", "sender")
