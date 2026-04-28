from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]


class UserSerializer(BaseUserSerializer):
    pass


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    DTO for user registration.

    Schema-level validation only. Business rules (uniqueness, side effects) live in
    `apps.users.services.create_user_services.create_user`.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "phone_number",
            "first_name",
            "last_name",
        ]

    def validate_email(self, value: str) -> str:
        return value.strip().lower()
