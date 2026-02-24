from __future__ import annotations

import os
import uuid

from django.conf import settings
from django.db import models

from apps.common.models.common_base_models import HatchUpBaseModel


def message_file_upload_to(instance: "Message", filename: str) -> str:
    safe_name = os.path.basename(filename or "")
    _, ext = os.path.splitext(safe_name)
    ext = (ext or "").lower()
    unique_id = uuid.uuid4().hex
    conversation_id = instance.conversation_id or "unknown"
    return f"messages/{conversation_id}/{unique_id}{ext}"


class Conversation(HatchUpBaseModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_conversations",
    )
    last_message_at = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ConversationParticipant",
        related_name="conversations",
    )

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ["-last_message_at", "-created_at"]

    def __str__(self) -> str:
        return f"Conversation {self.id}"


class ConversationParticipant(HatchUpBaseModel):
    conversation = models.ForeignKey(
        "messaging.Conversation",
        on_delete=models.CASCADE,
        related_name="participant_links",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_links",
    )

    class Meta:
        verbose_name = "Conversation Participant"
        verbose_name_plural = "Conversation Participants"
        constraints = [
            models.UniqueConstraint(
                fields=("conversation", "user"), name="uniq_conversation_participant"
            )
        ]

    def __str__(self) -> str:
        return f"Conversation {self.conversation_id} -> User {self.user_id}"


class Message(HatchUpBaseModel):
    conversation = models.ForeignKey(
        "messaging.Conversation",
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    content = models.TextField(blank=True)
    file = models.FileField(
        upload_to=message_file_upload_to,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Message {self.id} in Conversation {self.conversation_id}"
