from rest_framework import serializers

from apps.auth.services.otp_service import OTP_PURPOSE_LOGIN
from apps.auth.services.otp_service import OTP_PURPOSE_REGISTER


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    purpose = serializers.ChoiceField(
        choices=[OTP_PURPOSE_LOGIN, OTP_PURPOSE_REGISTER],
        write_only=True,
    )


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
    purpose = serializers.ChoiceField(
        choices=[OTP_PURPOSE_LOGIN, OTP_PURPOSE_REGISTER],
    )


class OTPTokenExchangeSerializer(serializers.Serializer):
    otp_verification_id = serializers.CharField()
    email = serializers.EmailField(required=False)


class OTPRequestSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)


class OTPVerifyResponseSerializer(serializers.Serializer):
    otp_verification_id = serializers.CharField(read_only=True)
