from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from habbits.models import Habbit
from users.models import User
from unittest.mock import patch
from habbits.tasks import send_notices
from datetime import timedelta


class HabbitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", telegram_id="12345"
        )

    def test_create_habit_valid(self):
        habit = Habbit.objects.create(
            place="Home",
            time=timezone.now(),
            action="Exercise",
            is_rewarding=False,
            reward_text="Watch TV",
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user,
        )
        self.assertEqual(habit.place, "Home")
        self.assertEqual(habit.user, self.user)

    def test_related_habit_and_reward_text_both_set(self):
        related_habit = Habbit.objects.create(
            place="Park",
            time=timezone.now(),
            action="Walk",
            is_rewarding=True,
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user,
        )
        with self.assertRaises(ValidationError):
            habit = Habbit(
                place="Home",
                time=timezone.now(),
                action="Exercise",
                is_rewarding=False,
                related_habit=related_habit,
                reward_text="Watch TV",
                periodicity_days=1,
                duration_seconds=60,
                is_public=False,
                user=self.user,
            )
            habit.full_clean()

    def test_neither_related_habit_nor_reward_text_set(self):
        with self.assertRaises(ValidationError):
            habit = Habbit(
                place="Home",
                time=timezone.now(),
                action="Exercise",
                is_rewarding=False,
                periodicity_days=1,
                duration_seconds=60,
                is_public=False,
                user=self.user,
            )
            habit.full_clean()

    def test_periodicity_days_validation(self):
        with self.assertRaises(ValidationError):
            habit = Habbit(
                place="Home",
                time=timezone.now(),
                action="Exercise",
                is_rewarding=False,
                reward_text="Watch TV",
                periodicity_days=0,
                duration_seconds=60,
                is_public=False,
                user=self.user,
            )
            habit.full_clean()

    def test_duration_seconds_validation(self):
        with self.assertRaises(ValidationError):
            habit = Habbit(
                place="Home",
                time=timezone.now(),
                action="Exercise",
                is_rewarding=False,
                reward_text="Watch TV",
                periodicity_days=1,
                duration_seconds=121,
                is_public=False,
                user=self.user,
            )
            habit.full_clean()


class PublicHabbitListAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", telegram_id="12345"
        )
        self.public_habit = Habbit.objects.create(
            place="Park",
            time=timezone.now(),
            action="Jogging",
            is_rewarding=False,
            reward_text="Ice cream",
            periodicity_days=1,
            duration_seconds=60,
            is_public=True,
            user=self.user,
        )
        self.private_habit = Habbit.objects.create(
            place="Home",
            time=timezone.now(),
            action="Reading",
            is_rewarding=False,
            reward_text="Relax",
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user,
        )

    def test_get_public_habits(self):
        response = self.client.get("/habbits/public/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["action"], "Jogging")


class HabbitViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", password="pass1", telegram_id="111"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass2", telegram_id="222"
        )
        self.habit1 = Habbit.objects.create(
            place="Home",
            time=timezone.now(),
            action="Exercise",
            is_rewarding=False,
            reward_text="Watch TV",
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user1,
        )
        self.habit2 = Habbit.objects.create(
            place="Office",
            time=timezone.now(),
            action="Work",
            is_rewarding=False,
            reward_text="Coffee",
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user2,
        )

    def test_list_habits(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/habbits/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Exercise")

    def test_create_habit(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "place": "Gym",
            "time": timezone.now().isoformat(),
            "action": "Workout",
            "is_rewarding": False,
            "reward_text": "Protein shake",
            "periodicity_days": 1,
            "duration_seconds": 90,
            "is_public": False,
        }
        response = self.client.post("/habbits/", data, format="json")
        self.assertEqual(response.status_code, 201)
        new_habit = Habbit.objects.get(action="Workout")
        self.assertEqual(new_habit.user, self.user1)

    def test_retrieve_habit_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/habbits/{self.habit1.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["action"], "Exercise")

    def test_retrieve_habit_non_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/habbits/{self.habit1.id}/")
        self.assertEqual(response.status_code, 404)

    def test_update_habit_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {"action": "Updated Exercise"}
        response = self.client.patch(f"/habbits/{self.habit1.id}/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.habit1.refresh_from_db()
        self.assertEqual(self.habit1.action, "Updated Exercise")

    def test_delete_habit_non_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/habbits/{self.habit1.id}/")
        self.assertEqual(response.status_code, 404)

    def test_pagination(self):
        self.client.force_authenticate(user=self.user1)
        Habbit.objects.filter(user=self.user1).exclude(
            id=self.habit1.id
        ).delete()  # Очищаем существующие привычки для user1, кроме той, что в setUp
        # Создаём 6 новых привычек
        for i in range(6):
            Habbit.objects.create(
                place=f"Place {i}",
                time=timezone.now(),
                action=f"Action {i}",
                is_rewarding=False,
                reward_text="Reward",
                periodicity_days=1,
                duration_seconds=60,
                is_public=False,
                user=self.user1,
            )
        # Проверяем, что в базе 7 привычек (1 из setUp + 6 новых)
        self.assertEqual(Habbit.objects.filter(user=self.user1).count(), 7)
        response = self.client.get("/habbits/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)  # Пагинация должна вернуть 5
        self.assertIsNotNone(response.data["next"])  # Должна быть следующая страница


class SendNoticesTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass", telegram_id="12345"
        )
        now = timezone.datetime(
            2023, 1, 1, 12, 0, 0, tzinfo=timezone.get_current_timezone()
        )
        self.habit = Habbit.objects.create(
            place="Home",
            time=now,
            action="Exercise",
            is_rewarding=False,
            reward_text="Watch TV",
            periodicity_days=1,
            duration_seconds=60,
            is_public=False,
            user=self.user,
        )
        self.habit.created_at = now - timedelta(days=1)
        self.habit.save()

    @patch("habbits.services.send_telegram_message")
    @patch("django.utils.timezone.now")
    def test_send_notices_habit_not_due_time(self, mock_now, mock_send):
        now = timezone.datetime(
            2023, 1, 1, 12, 0, 0, tzinfo=timezone.get_current_timezone()
        )
        mock_now.return_value = now
        self.habit.time = now + timedelta(minutes=1)
        self.habit.save()
        send_notices()
        mock_send.assert_not_called()

    @patch("habbits.services.send_telegram_message")
    @patch("django.utils.timezone.now")
    def test_send_notices_habit_not_due_periodicity(self, mock_now, mock_send):
        now = timezone.datetime(
            2023, 1, 1, 12, 0, 0, tzinfo=timezone.get_current_timezone()
        )
        mock_now.return_value = now
        self.habit.created_at = now - timedelta(days=2)
        self.habit.periodicity_days = 3
        self.habit.save()
        send_notices()
        mock_send.assert_not_called()  # 2 days % 3 != 0, no notification
