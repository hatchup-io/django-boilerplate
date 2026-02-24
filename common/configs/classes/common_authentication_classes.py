from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

User = get_user_model()


class HatchupJWTAuthentication(JWTAuthentication):
    def authenticate(self, request) -> tuple | None:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "") or request.META.get(
            "Authorization", ""
        )
        if not auth_header:
            return None

        try:
            header = auth_header.split()
            if not header or len(header) != 2:
                msg = "Invalid authorization header format."
                raise AuthenticationFailed(msg)

            raw_token = header[1]
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user_object(validated_token)
            request.user = user
            return user, validated_token
        except TokenError as err:
            msg = "Invalid token"
            raise AuthenticationFailed(msg) from err
        except InvalidToken as err:
            msg = "Token is invalid or expired"
            raise AuthenticationFailed(msg) from err
        except AuthenticationFailed:
            raise
        except Exception as err:
            msg = "Authentication failed"
            raise AuthenticationFailed(msg) from err

    def get_user_object(self, validated_token):
        decoded_payload = validated_token.payload

        try:
            user = User.objects.get(id=decoded_payload.get("user_id"), is_active=True)
        except User.DoesNotExist as err:
            msg = "User not found"
            raise AuthenticationFailed(msg) from err

        return user


class HatchupAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = HatchupJWTAuthentication
    name = "Hatchup_auth"
    match_subclasses = True
    priority = -1

    def get_security_definition(self, auto_schema):
        auth_header_types = jwt_api_settings.AUTH_HEADER_TYPES
        token_prefix = (
            auth_header_types[0]
            if isinstance(auth_header_types, (list, tuple))
            else auth_header_types
        )
        return build_bearer_security_scheme_object(
            header_name="Authorization",
            token_prefix=token_prefix,
        )
