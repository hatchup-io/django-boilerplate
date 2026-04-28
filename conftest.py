from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db):
    from apps.users.tests.factories import UserFactory

    return UserFactory()


@pytest.fixture
def auth_client(api_client: APIClient, user) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client
