from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from apps.auth.configs.constants.roles import RoleName

User = get_user_model()


def make_user(
    *,
    email: str,
    phone: str,
    first: str = "T",
    last: str = "U",
    password: str = "pass1234",
) -> User:
    user = User.objects.create(
        email=email,
        phone_number=phone,
        first_name=first,
        last_name=last,
    )
    user.set_password(password)
    user.save()
    return user


class MessagingConversationRuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for role in RoleName:
            Group.objects.get_or_create(name=role.value)

    def setUp(self):
        self.client = APIClient()

        self.admin = make_user(email="admin@test.com", phone="1000000100")
        self.admin.groups.add(Group.objects.get(name=RoleName.ADMIN.value))

        self.startup = make_user(email="startup@test.com", phone="1000000101")
        self.startup.groups.add(Group.objects.get(name=RoleName.STARTUP.value))

        self.investor = make_user(email="investor@test.com", phone="1000000102")
        self.investor.groups.add(Group.objects.get(name=RoleName.INVESTOR.value))

    def _payload_data(self, response):
        body = response.json()
        return body.get("data", body)

    def test_startup_can_create_conversation_with_admin(self):
        self.client.force_authenticate(user=self.startup)
        res = self.client.post(
            "/api/messaging/conversations/",
            {"participant_id": self.admin.id},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        data = self._payload_data(res)
        participant_ids = {p["id"] for p in data["participants"]}
        self.assertEqual(participant_ids, {self.startup.id, self.admin.id})

    def test_investor_can_create_conversation_with_admin(self):
        self.client.force_authenticate(user=self.investor)
        res = self.client.post(
            "/api/messaging/conversations/",
            {"participant_id": self.admin.id},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        data = self._payload_data(res)
        participant_ids = {p["id"] for p in data["participants"]}
        self.assertEqual(participant_ids, {self.investor.id, self.admin.id})

    def test_startup_and_investor_cannot_connect(self):
        self.client.force_authenticate(user=self.startup)
        res = self.client.post(
            "/api/messaging/conversations/",
            {"participant_id": self.investor.id},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
