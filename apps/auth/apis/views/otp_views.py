from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.auth.apis.serializers.auth_authentication_serializers import AuthenticationTokensSerializer
from apps.auth.apis.serializers.auth_otp_serializers import OTPRequestSerializer
from apps.auth.apis.serializers.auth_otp_serializers import OTPRequestSuccessSerializer
from apps.auth.apis.serializers.auth_otp_serializers import OTPTokenExchangeSerializer
from apps.auth.apis.serializers.auth_otp_serializers import OTPVerifyResponseSerializer
from apps.auth.apis.serializers.auth_otp_serializers import OTPVerifySerializer
from apps.auth.services.auth_token_generator_services import generate_token_for_user
from apps.auth.services.otp_service import OTP_PURPOSE_LOGIN
from apps.auth.services.otp_service import OTP_PURPOSE_REGISTER
from apps.auth.services.otp_service import consume_verification_id
from apps.auth.services.otp_service import generate_otp
from apps.auth.services.otp_service import send_otp_email
from apps.auth.services.otp_service import store_otp
from apps.auth.services.otp_service import verify_otp_and_issue_verification_id
from apps.common.apis.views.common_base_views import HatchupAPIView

User = get_user_model()


class OTPRequestView(HatchupAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication - OTP"],
        summary="Request OTP",
        description="Send a one-time password to the given email for login or register.",
        request=OTPRequestSerializer,
        responses={200: OTPRequestSuccessSerializer()},
    )
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        purpose = serializer.validated_data["purpose"]
        if purpose == OTP_PURPOSE_LOGIN:
            if not User.objects.filter(email__iexact=email).exists():
                return Response(
                    {"detail": "No user with this email exists."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif purpose == OTP_PURPOSE_REGISTER:
            if User.objects.filter(email__iexact=email).exists():
                return Response(
                    {"detail": "A user with this email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        otp = generate_otp()
        store_otp(email, otp, purpose)
        send_otp_email(email, otp, purpose)
        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)


class OTPVerifyView(HatchupAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication - OTP"],
        summary="Verify OTP",
        description="Verify OTP and return a short-lived otp_verification_id for register or token exchange.",
        request=OTPVerifySerializer,
        responses={200: OTPVerifyResponseSerializer()},
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].strip().lower()
        otp = serializer.validated_data["otp"].strip()
        purpose = serializer.validated_data["purpose"]
        verification_id = verify_otp_and_issue_verification_id(email, otp, purpose)
        if verification_id is None:
            return Response(
                {"detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"otp_verification_id": verification_id}, status=status.HTTP_200_OK)


class OTPTokenExchangeView(HatchupAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication - OTP"],
        summary="Exchange OTP verification for tokens",
        description="Exchange a valid otp_verification_id (from verify step) for JWT tokens.",
        request=OTPTokenExchangeSerializer,
        responses={200: AuthenticationTokensSerializer()},
    )
    def post(self, request):
        serializer = OTPTokenExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification_id = (serializer.validated_data["otp_verification_id"] or "").strip()
        payload = consume_verification_id(verification_id)
        if payload is None:
            return Response(
                {"detail": "Invalid or expired verification."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payload.get("purpose") != OTP_PURPOSE_LOGIN:
            return Response(
                {"detail": "Verification was not for login."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = payload.get("email", "").strip().lower()
        if serializer.validated_data.get("email"):
            if serializer.validated_data["email"].strip().lower() != email:
                return Response(
                    {"detail": "Email does not match verification."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        tokens = generate_token_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)
