from __future__ import annotations

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.services.roles import has_any_role, is_platform_admin
from notification.apis.permissions import NotificationEndpointPermission
from notification.apis.serializers import (
    MarkAsReadSerializer,
    NotificationAdminCreateSerializer,
    NotificationSerializer,
)
from notification.models.notification_models import Notification, NotificationUser

from common.apis.views.common_base_views import HatchupModelViewset


def _is_admin_action(view) -> bool:
    action = getattr(view, "action", None)
    return action in {"create", "update", "partial_update", "destroy"}


def _is_admin_user(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (is_platform_admin(user) or has_any_role(user, ["Admin"]))
    )


@extend_schema_view(
    list=extend_schema(
        tags=["Notifications"],
        summary="List notifications",
        description=(
            "List notifications visible to the authenticated user (global, direct targets, "
            "or role-based). Admins see all notifications."
        ),
        responses={200: NotificationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Notifications"],
        summary="Retrieve a notification",
        description="Retrieve a notification by ID. Non-admins only see notifications visible to them.",
        responses={200: NotificationSerializer()},
    ),
    create=extend_schema(
        tags=["Notifications"],
        summary="Create notification (Admin)",
        description=(
            "Create a notification and broadcast to audience: set is_global=True for everyone, "
            "target_user_ids for specific users, and/or target_role_names for role-based delivery. Admin only."
        ),
        request=NotificationAdminCreateSerializer(),
        responses={201: NotificationAdminCreateSerializer()},
    ),
    partial_update=extend_schema(
        tags=["Notifications"],
        summary="Partially update notification (Admin)",
        description="Partially update a notification. Admin only.",
        request=NotificationAdminCreateSerializer(partial=True),
        responses={200: NotificationAdminCreateSerializer()},
    ),
    update=extend_schema(
        tags=["Notifications"],
        summary="Update notification (Admin)",
        description="Update a notification. Admin only.",
        request=NotificationAdminCreateSerializer(),
        responses={200: NotificationAdminCreateSerializer()},
    ),
    destroy=extend_schema(
        tags=["Notifications"],
        summary="Delete notification (Admin)",
        description="Delete a notification. Admin only.",
        responses={204: None},
    ),
)
class NotificationViewSet(HatchupModelViewset):
    permission_classes = [IsAuthenticated, NotificationEndpointPermission]

    def get_queryset(self):
        user = self.request.user
        if _is_admin_user(user):
            qs = Notification.objects.all()
        else:
            qs = Notification.visible_to_user_queryset(user=user)
        if not _is_admin_action(self):
            qs = qs.prefetch_related(
                Prefetch(
                    "user_states",
                    queryset=NotificationUser.objects.filter(user=user),
                    to_attr="state_for_user",
                )
            )
        return qs

    def get_serializer_class(self):
        if _is_admin_action(self):
            return NotificationAdminCreateSerializer
        return NotificationSerializer

    @extend_schema(
        tags=["Notifications"],
        summary="Unread count",
        description="Return the number of notifications visible to the user that are not yet read.",
        responses={
            200: {
                "type": "object",
                "properties": {"unread_count": {"type": "integer"}},
                "required": ["unread_count"],
            }
        },
    )
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        user = request.user
        visible = Notification.visible_to_user_queryset(user=user)
        unread = (
            visible.exclude(user_states__user=user, user_states__read_at__isnull=False)
            .distinct()
            .count()
        )
        return Response({"unread_count": unread})

    @extend_schema(
        tags=["Notifications"],
        summary="Mark as read",
        description="Mark a single notification as read (or unread) for the current user.",
        request=MarkAsReadSerializer(),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "read_at": {
                        "type": "string",
                        "format": "date-time",
                        "nullable": True,
                    },
                    "is_read": {"type": "boolean"},
                },
                "required": ["id", "read_at", "is_read"],
            },
        },
    )
    @action(detail=True, methods=["post"], url_path="read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        ser = MarkAsReadSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)
        state = ser.save(user=request.user, notification=notification)
        return Response(
            {
                "id": notification.id,
                "read_at": state.read_at,
                "is_read": bool(state.read_at),
            }
        )

    @extend_schema(
        tags=["Notifications"],
        summary="Mark all as read",
        description="Mark all notifications visible to the user as read.",
        responses={
            200: {
                "type": "object",
                "properties": {"marked_read": {"type": "integer"}},
                "required": ["marked_read"],
            },
        },
    )
    @action(detail=False, methods=["post"], url_path="read-all")
    def mark_all_read(self, request):
        user = request.user
        now = timezone.now()

        visible_ids = list(
            Notification.visible_to_user_queryset(user=user).values_list(
                "id", flat=True
            )
        )
        if not visible_ids:
            return Response({"marked_read": 0})

        existing_states = NotificationUser.objects.filter(
            user=user, notification_id__in=visible_ids
        )

        existing_by_notif_id = {
            s.notification_id: s
            for s in existing_states.only("id", "notification_id", "read_at")
        }

        to_create = []
        to_update = []
        for nid in visible_ids:
            st = existing_by_notif_id.get(nid)
            if not st:
                to_create.append(
                    NotificationUser(user=user, notification_id=nid, read_at=now)
                )
            elif st.read_at is None:
                st.read_at = now
                to_update.append(st)

        with transaction.atomic():
            if to_create:
                NotificationUser.objects.bulk_create(to_create, ignore_conflicts=True)
            if to_update:
                NotificationUser.objects.bulk_update(
                    to_update, ["read_at", "updated_at"]
                )

        return Response({"marked_read": len(to_create) + len(to_update)})
