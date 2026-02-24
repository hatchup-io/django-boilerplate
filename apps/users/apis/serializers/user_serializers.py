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

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "This email cannot be used for registration."
            )
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data["email"]
        return User.objects.create_user(
            email=email, password=password, **validated_data
        )
