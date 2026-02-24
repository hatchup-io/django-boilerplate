from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers

from apps.common.apis.serializers.fields import Base64FileField
from apps.auth.services.roles import get_user_roles, is_platform_admin
from apps.messaging.models.messaging_models import (
    Conversation,
    ConversationParticipant,
    Message,
)

User = get_user_model()


def _role_flags(user) -> tuple[bool, bool, bool]:
    roles = get_user_roles(user)
    is_admin = bool(is_platform_admin(user) or "Admin" in roles)
    is_startup = "Startup" in roles
    is_investor = "Investor" in roles
    return is_admin, is_startup, is_investor


def _allowed_conversation(user_a, user_b) -> bool:
    a_admin, a_startup, a_investor = _role_flags(user_a)
    b_admin, b_startup, b_investor = _role_flags(user_b)

    if a_admin and b_admin:
        return False
    if a_admin:
        return b_startup or b_investor
    if b_admin:
        return a_startup or a_investor
    return False


class UserSummarySerializer(serializers.ModelSerializer):
    role_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role_names")

    def get_role_names(self, obj) -> list[str]:
        return list(obj.groups.values_list("name", flat=True))


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ("id", "participants", "last_message_at", "created_at")


class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(write_only=True, min_value=1)
    participants = UserSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = (
            "id",
            "participant_id",
            "participants",
            "last_message_at",
            "created_at",
        )
        read_only_fields = ("id", "participants", "last_message_at", "created_at")

    def validate_participant_id(self, value: int) -> int:
        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.id == value:
            raise serializers.ValidationError(
                "You cannot start a conversation with yourself."
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        if not request or not getattr(request, "user", None):
            raise serializers.ValidationError("Request context is required.")

        participant_id = attrs.get("participant_id")
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"participant_id": "User not found."})

        if not _allowed_conversation(request.user, participant):
            raise serializers.ValidationError(
                "Conversations are only allowed between admin and startup or admin and investor."
            )

        attrs["participant"] = participant
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        participant = validated_data.pop("participant")

        existing = (
            Conversation.objects.filter(participants__id=request.user.id)
            .filter(participants__id=participant.id)
            .annotate(participant_count=Count("participants", distinct=True))
            .filter(participant_count=2)
            .first()
        )
        if existing:
            self._existing = True
            return existing

        conversation = Conversation.objects.create(created_by=request.user)
        ConversationParticipant.objects.bulk_create(
            [
                ConversationParticipant(conversation=conversation, user=request.user),
                ConversationParticipant(conversation=conversation, user=participant),
            ],
            ignore_conflicts=True,
        )
        return conversation


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSummarySerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "conversation", "sender", "content", "file", "created_at")
        read_only_fields = ("id", "created_at", "sender", "conversation")


class MessageCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=False, allow_blank=True)
    file = Base64FileField(required=False, allow_null=True)

    class Meta:
        model = Message
        fields = ("id", "content", "file", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        conversation = self.context.get("conversation")
        if not request or not conversation:
            raise serializers.ValidationError("Request context is required.")

        is_participant = ConversationParticipant.objects.filter(
            conversation=conversation, user=request.user
        ).exists()
        if not is_participant:
            raise serializers.ValidationError(
                "You are not a participant in this conversation."
            )

        content = attrs.get("content", "")
        file_obj = attrs.get("file")
        if not content and not file_obj:
            raise serializers.ValidationError(
                "Message must include content or a file attachment."
            )
        attrs["content"] = content
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        conversation = self.context["conversation"]
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            **validated_data,
        )
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=["last_message_at", "updated_at"])
        return message
