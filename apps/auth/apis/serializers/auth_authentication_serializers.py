from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.auth.services.auth_token_generator_services import generate_token_for_user


class TokenObtainSerializer(TokenObtainPairSerializer):
    """Obtain JWT tokens with roles and username on payload; uses generate_token_for_user."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["roles"] = [role.name for role in user.roles.all()]
        token["username"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        return generate_token_for_user(self.user)


class AuthenticationTokensSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
