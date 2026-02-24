from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.common.apis.views.common_base_views import HatchupAPIView
from apps.users.apis.serializers.user_serializers import (
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterAPIView(HatchupAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    @extend_schema(
        tags=["Users"],
        summary="Register a new user",
        request=UserRegisterSerializer,
        responses={201: UserSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )


class CurrentUserAPIView(HatchupAPIView):
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Users"],
        summary="Get current authenticated user",
        responses={200: UserSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK,
        )
