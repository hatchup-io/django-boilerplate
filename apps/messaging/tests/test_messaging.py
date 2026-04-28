from __future__ import annotations

import pytest
from django.contrib.auth.models import Group

from apps.auth.configs.constants.roles import RoleName
from apps.users.models.users_role_models import UserRole
from apps.users.tests.factories import UserFactory


def _assign_role(user, role_name: RoleName) -> None:
    UserRole.objects.create(user=user, role=Group.objects.get(name=role_name.value))


pytestmark = pytest.mark.django_db


def _payload_data(response):
    body = response.json()
    return body.get("data", body)


@pytest.fixture
def role_groups():
    for role in RoleName:
        Group.objects.get_or_create(name=role.value)


@pytest.fixture
def admin_user(role_groups):
    user = UserFactory(email="admin@test.com")
    _assign_role(user, RoleName.ADMIN)
    return user


@pytest.fixture
def startup_user(role_groups):
    user = UserFactory(email="startup@test.com")
    _assign_role(user, RoleName.STARTUP)
    return user


@pytest.fixture
def investor_user(role_groups):
    user = UserFactory(email="investor@test.com")
    _assign_role(user, RoleName.INVESTOR)
    return user


def test_startup_can_create_conversation_with_admin(api_client, startup_user, admin_user):
    api_client.force_authenticate(user=startup_user)
    response = api_client.post(
        "/api/messaging/conversations/",
        {"participant_id": admin_user.id},
        format="json",
    )

    assert response.status_code == 201
    data = _payload_data(response)
    assert {p["id"] for p in data["participants"]} == {startup_user.id, admin_user.id}


def test_investor_can_create_conversation_with_admin(api_client, investor_user, admin_user):
    api_client.force_authenticate(user=investor_user)
    response = api_client.post(
        "/api/messaging/conversations/",
        {"participant_id": admin_user.id},
        format="json",
    )

    assert response.status_code == 201
    data = _payload_data(response)
    assert {p["id"] for p in data["participants"]} == {investor_user.id, admin_user.id}


def test_startup_and_investor_cannot_connect(api_client, startup_user, investor_user):
    api_client.force_authenticate(user=startup_user)
    response = api_client.post(
        "/api/messaging/conversations/",
        {"participant_id": investor_user.id},
        format="json",
    )

    assert response.status_code == 400
