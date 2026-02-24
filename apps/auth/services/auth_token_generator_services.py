from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models.users_user_models import User


def generate_token_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    refresh["roles"] = [role.name for role in user.roles.all()]
    refresh["username"] = user.email

    access["roles"] = [role.name for role in user.roles.all()]
    access["username"] = user.email
    return {
        "refresh": str(refresh),
        "access": str(access),
    }
