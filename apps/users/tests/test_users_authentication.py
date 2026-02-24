from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class UserAuthenticationBoilerplateTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        payload = {
            "email": "new.user@test.com",
            "password": "securepass123",
            "phone_number": "1000000000",
            "first_name": "New",
            "last_name": "User",
        }

        response = self.client.post("/api/users/register/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], payload["email"])
        self.assertNotIn("password", response.json())

        created_user = User.objects.get(email=payload["email"])
        self.assertTrue(created_user.check_password(payload["password"]))

    def test_login_and_refresh_tokens(self):
        user = User(
            email="member@test.com",
            phone_number="1000000001",
            first_name="Member",
            last_name="User",
        )
        user.set_password("strongpass123")
        user.save()

        login_response = self.client.post(
            "/api/auth/token/",
            {"email": user.email, "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.json())
        self.assertIn("refresh", login_response.json())

        refresh_response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": login_response.json()["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.json())

    def test_current_user_requires_authentication(self):
        response = self.client.get("/api/users/me/")
        self.assertIn(response.status_code, (401, 403))

    def test_current_user_returns_authenticated_user(self):
        user = User.objects.create(
            email="current@test.com",
            phone_number="1000000002",
            first_name="Current",
            last_name="User",
        )

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], user.email)
