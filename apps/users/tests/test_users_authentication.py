from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.users.tests.factories import UserFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


def _payload_data(response):
    body = response.json()
    return body.get("data", body)


def test_register_user(api_client):
    payload = {
        "email": "new.user@test.com",
        "password": "securepass123",
        "phone_number": "1000000000",
        "first_name": "New",
        "last_name": "User",
    }

    response = api_client.post("/api/users/register/", payload, format="json")

    assert response.status_code == 201
    data = _payload_data(response)
    assert data["email"] == payload["email"]
    assert "password" not in data

    created_user = User.objects.get(email=payload["email"])
    assert created_user.check_password(payload["password"])


def test_login_and_refresh_tokens(api_client):
    user = UserFactory(email="member@test.com", password="strongpass123")

    login_response = api_client.post(
        "/api/auth/token/",
        {"email": user.email, "password": "strongpass123"},
        format="json",
    )
    assert login_response.status_code == 200
    login_data = _payload_data(login_response)
    assert "access" in login_data
    assert "refresh" in login_data

    refresh_response = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": login_data["refresh"]},
        format="json",
    )
    assert refresh_response.status_code == 200
    assert "access" in _payload_data(refresh_response)


def test_current_user_requires_authentication(api_client):
    response = api_client.get("/api/users/me/")
    assert response.status_code in (401, 403)


def test_current_user_returns_authenticated_user(auth_client, user):
    response = auth_client.get("/api/users/me/")

    assert response.status_code == 200
    assert _payload_data(response)["email"] == user.email
