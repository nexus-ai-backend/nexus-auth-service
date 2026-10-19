from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
# Create your tests here.

class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="Test-Password-123!",
        )
        self.assertTrue(user.pk)
        self.assertTrue(user.check_password("Test-Password-123!"))

    def test_check_password_is_not_stored_as_plain_text(self):
        user = User.objects.create_user(
            username="password_test",
            password="Test-Password-123!",
        )

        self.assertNotEqual(user.password, "Test-Password-123!")


class UserRegistrationAPITests(APITestCase):

    def test_register_user_successfully(self):
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
        }

        response = self.client.post(
            "/api/auth/register/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )
        self.assertNotIn("password", response.data)

        user = User.objects.get(username="testuser")
        self.assertTrue(
            user.check_password("StrongPass123!")
        )

    def test_duplicate_username_rejected(self):
        User.objects.create_user(
            username="testuser",
            email="first@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "email": "second@example.com",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.filter(username="testuser").count(), 1)

    def test_short_password_length_rejected(self):

        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "Avinash",
                "email": "a@b.com",
                "password": "1234"
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(username="Avinash").exists()
        )


class UserAuthenticationAPITests(APITestCase):

    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="avinash",
            email="a@b.com",
            password=self.password
        )

    def test_login_returns_token(self):
        reponse = self.client.post(
            "/api/auth/login/",
            {
                "username": "avinash",
                "password": self.password
            },
            format="json",
        )

        self.assertEqual(reponse.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", reponse.data)
        self.assertIn("refresh_token", reponse.data)

    def test_login_rejecting_wrong_password(self):
        respose = self.client.post(
            "/api/auth/login/",
            {
                "username": "avinash",
                "password": "WrongPass123!"
            },
            format="json",
        )

        self.assertEqual(respose.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", respose.data)

    def test_me_rejects_missing_token(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_accepts_valid_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "username": "avinash",
                "password": self.password,
            },
            format="json",
        )
        
        access = login_response.data["access_token"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "avinash")

    def test_refresh_returns_access_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "username": "avinash",
                "password": self.password,
            },
            format="json",
        )
        refresh = login_response.data["refresh_token"]

        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(
            "/api/auth/token/refresh/",
            {"refresh": "not-a-valid-token"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )