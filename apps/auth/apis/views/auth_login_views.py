from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from apps.auth.apis.serializers.auth_authentication_serializers import (
    AuthenticationTokensSerializer,
    RefreshTokenSerializer,
    TokenObtainSerializer,
)
from apps.common.apis.views.common_base_views import HatchupAPIView
from drf_spectacular.utils import extend_schema


class LoginAPIView(HatchupAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = TokenObtainSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Obtain JWT tokens",
        request=TokenObtainSerializer,
        responses={200: AuthenticationTokensSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshTokenAPIView(HatchupAPIView):
    serializer_class = TokenRefreshSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh JWT access token",
        request=TokenRefreshSerializer,
        responses={200: RefreshTokenSerializer()},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
