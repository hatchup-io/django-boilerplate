from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.common.models.common_base_models import HatchUpBaseModel
from apps.notification.configs.constants.notification_enums import (
    NotificationCategoryChoices,
)


class Notification(HatchUpBaseModel):
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(
        max_length=16,
        choices=NotificationCategoryChoices.choices,
        default=NotificationCategoryChoices.ALERT,
    )
    data = models.JSONField(default=dict, blank=True)

    is_global = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_notifications",
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at <= timezone.now())

    @classmethod
    def visible_to_user_queryset(cls, user) -> models.QuerySet["Notification"]:
        """
        Return notifications visible to `user` (by global/user/role targets), excluding expired.
        """

        if not getattr(user, "is_authenticated", False):
            return cls.objects.none()

        roles = user.groups.all()
        # Direct user audience is represented by a NotificationUser row for that user.
        q = Q(is_global=True) | Q(user_states__user=user)
        if roles:
            q |= Q(role_targets__role__in=roles)

        qs = cls.objects.filter(q).distinct()
        # Exclude expired:
        qs = qs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        return qs


class NotificationRoleTarget(HatchUpBaseModel):
    notification = models.ForeignKey(
        "notification.Notification",
        on_delete=models.CASCADE,
        related_name="role_targets",
    )
    role = models.ForeignKey(
        Group,
        verbose_name=_("Role"),
        on_delete=models.CASCADE,
        related_name="role_targets",
    )

    class Meta:
        verbose_name = "Notification Role Target"
        verbose_name_plural = "Notification Role Targets"
        constraints = [
            models.UniqueConstraint(
                fields=("notification", "role"), name="uniq_notification_role_target"
            )
        ]

    def __str__(self) -> str:
        return f"{self.notification_id} -> role:{self.role_id_id}"


class NotificationUser(HatchUpBaseModel):
    notification = models.ForeignKey(
        "notification.Notification",
        on_delete=models.CASCADE,
        related_name="user_states",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="notification_states",
    )

    read_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notification User"
        verbose_name_plural = "Notification Users"
        constraints = [
            models.UniqueConstraint(
                fields=("notification", "user"), name="uniq_notification_user"
            )
        ]

    def __str__(self) -> str:
        if hasattr(self.user, "full_name"):
            user_repr = self.user.full_name
        else:
            user_repr = str(self.user_id)
        return f"state notif:{self.notification_id} user:{user_repr}"
