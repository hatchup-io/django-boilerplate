from __future__ import annotations

from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import serializers

from notification.configs.constants.notification_enums import (
    NotificationCategoryChoices,
)
from notification.models.notification_models import (
    Notification,
    NotificationRoleTarget,
    NotificationUser,
)
from users.models.users_user_models import User


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "category",
            "data",
            "created_at",
            "expires_at",
            "is_global",
            "is_read",
            "read_at",
        )

    def _state(self, obj: Notification) -> NotificationUser | None:
        # View prefetches `user_states` filtered to current user into `state_for_user`.
        state_list = getattr(obj, "state_for_user", None)
        if state_list:
            return state_list[0]
        return None

    def get_is_read(self, obj: Notification) -> bool:
        st = self._state(obj)
        return bool(st and st.read_at)

    def get_read_at(self, obj: Notification):
        st = self._state(obj)
        return st.read_at if st else None


class NotificationAdminCreateSerializer(serializers.ModelSerializer):
    """
    Admin payload supports targeting:
    - `is_global=True` -> everyone
    - `target_user_ids=[...]` -> specific users
    - `target_role_names=[...]` -> role-based (Django Group names)
    """

    category = serializers.ChoiceField(
        choices=NotificationCategoryChoices.choices, required=False
    )
    target_user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, allow_empty=True
    )
    target_role_names = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "category",
            "data",
            "is_global",
            "expires_at",
            "target_user_ids",
            "target_role_names",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        is_global = bool(attrs.get("is_global"))
        target_user_ids = attrs.get("target_user_ids") or []
        target_role_names = [
            str(x).strip()
            for x in (attrs.get("target_role_names") or [])
            if str(x).strip()
        ]

        if not is_global and not target_user_ids and not target_role_names:
            raise serializers.ValidationError(
                "Provide at least one audience: is_global=true, target_user_ids, or target_role_names."
            )

        # Normalize:
        attrs["target_role_names"] = target_role_names
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        created_by = getattr(request, "user", None)

        target_user_ids = validated_data.pop("target_user_ids", []) or []
        target_role_names = validated_data.pop("target_role_names", []) or []

        notif = Notification.objects.create(created_by=created_by, **validated_data)

        if target_user_ids:
            users = list(User.objects.filter(id__in=target_user_ids))
            # Create per-user rows (unread by default) to represent direct audience.
            NotificationUser.objects.bulk_create(
                [NotificationUser(notification=notif, user=u) for u in users],
                ignore_conflicts=True,
            )

        if target_role_names:
            roles = list(Group.objects.filter(name__in=target_role_names))
            NotificationRoleTarget.objects.bulk_create(
                [NotificationRoleTarget(notification=notif, role=r) for r in roles],
                ignore_conflicts=True,
            )

        return notif


class MarkAsReadSerializer(serializers.Serializer):
    read = serializers.BooleanField(default=True, required=False)

    def save(self, *, user: User, notification: Notification) -> NotificationUser:
        read = bool(self.validated_data.get("read", True))
        now = timezone.now()
        state, _ = NotificationUser.objects.get_or_create(
            user=user, notification=notification
        )
        state.read_at = now if read else None
        state.save(update_fields=["read_at", "updated_at"])
        return state
