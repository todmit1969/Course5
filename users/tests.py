from django.test import TestCase
from django.db import IntegrityError
from users.models import User
from rest_framework.test import APITestCase, APIClient


class UserModelTest(TestCase):
    def test_telegram_id_unique(self):
        User.objects.create_user(
            username="user1", password="pass1", telegram_id="12345"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="user2", password="pass2", telegram_id="12345"
            )

    def test_create_user_with_telegram_id(self):
        user = User.objects.create_user(
            username="testuser", password="testpass", telegram_id="54321"
        )
        self.assertEqual(user.telegram_id, "54321")
        self.assertTrue(user.check_password("testpass"))


class UserRegistrationAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user_valid_data(self):
        data = {"username": "newuser", "password": "newpass", "telegram_id": "54321"}
        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username="newuser")
        self.assertTrue(user.check_password("newpass"))
        self.assertEqual(user.telegram_id, "54321")
        self.assertTrue(user.is_active)

    def test_register_user_missing_fields(self):
        data = {"username": "newuser"}
        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertIn("telegram_id", response.data)

    def test_register_duplicate_telegram_id(self):
        User.objects.create_user(
            username="user1", password="pass1", telegram_id="12345"
        )
        data = {"username": "user2", "password": "pass2", "telegram_id": "12345"}
        response = self.client.post("/users/register/", data, format="json")
        self.assertEqual(response.status_code, 400)