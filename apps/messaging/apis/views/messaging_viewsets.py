from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.common.apis.views.common_base_views import HatchupModelViewset
from apps.messaging.apis.serializers.messaging_serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)
from apps.messaging.models.messaging_models import Conversation


@extend_schema_view(
    list=extend_schema(
        tags=["Messaging"],
        summary="List conversations",
        description="List conversations for the authenticated user.",
        responses={200: ConversationSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Messaging"],
        summary="Retrieve conversation",
        description="Retrieve a conversation the authenticated user participates in.",
        responses={200: ConversationSerializer()},
    ),
    create=extend_schema(
        tags=["Messaging"],
        summary="Create conversation",
        description=(
            "Create a conversation between admin and startup or admin and investor. "
            "Investor and startup cannot start a conversation."
        ),
        request=ConversationCreateSerializer(),
        responses={200: ConversationSerializer(), 201: ConversationSerializer()},
    ),
)
class ConversationViewSet(HatchupModelViewset):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects.filter(participants__id=user.id)
            .prefetch_related("participants__groups")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        status_code = (
            status.HTTP_200_OK
            if getattr(serializer, "_existing", False)
            else status.HTTP_201_CREATED
        )
        response_serializer = ConversationSerializer(
            conversation, context=self.get_serializer_context()
        )
        return Response(response_serializer.data, status=status_code)

    @extend_schema(
        tags=["Messaging"],
        summary="List conversation messages",
        description="List messages in a conversation for a participant.",
        responses={200: MessageSerializer(many=True)},
        methods=["GET"],
    )
    @extend_schema(
        tags=["Messaging"],
        summary="Send message",
        description="Send a message in a conversation.",
        request=MessageCreateSerializer(),
        responses={201: MessageSerializer()},
        methods=["POST"],
    )
    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        conversation = self.get_object()

        if request.method == "GET":
            qs = (
                conversation.messages.select_related("sender")
                .prefetch_related("sender__groups")
                .order_by("created_at")
            )
            page = self.paginate_queryset(qs)
            serializer = MessageSerializer(
                page if page is not None else qs,
                many=True,
                context=self.get_serializer_context(),
            )
            if page is not None:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)

        context = self.get_serializer_context()
        context["conversation"] = conversation
        serializer = MessageCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(
            MessageSerializer(message, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )
