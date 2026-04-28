"""User creation business logic."""

from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.common.exceptions import ConflictError

User = get_user_model()


def create_user(
    *,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    phone_number: str = "",
):
    """
    Create a new user.

    Raises:
        ConflictError: if a user with this email already exists.
    """
    email_clean = email.strip().lower()
    if User.objects.filter(email__iexact=email_clean).exists():
        raise ConflictError("This email cannot be used for registration.")
    return User.objects.create_user(
        email=email_clean,
        password=password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
    )
