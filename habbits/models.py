from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from users.models import User


class Habbit(models.Model):
    place = models.CharField(
        max_length=150, help_text="Введите место для выполнения привычки"
    )
    time = models.DateTimeField(
        help_text="Введите время и дату выполнения привычки",
    )
    action = models.CharField(
        max_length=200,
        help_text="Введите действие, которое представляет собой привычка",
    )
    is_rewarding = models.BooleanField(
        default=False, help_text="Укажите, если это приятная привычка"
    )
    related_habit = models.ForeignKey(
        to="self",
        help_text="Укажите привычку, связанную с новой привычкой",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    periodicity_days = models.IntegerField(
        help_text="Периодичность привычки в днях",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
    )
    reward_text = models.CharField(
        max_length=150,
        help_text="Укажите награду после выполнения привычки",
        blank=True,
        null=True,
    )
    duration_seconds = models.IntegerField(
        help_text="Укажите продолжительность выполнения привычки (в секундах, максимум 120)",
        validators=[MinValueValidator(1), MaxValueValidator(120)],
    )
    is_public = models.BooleanField(
        default=False, help_text="Укажите, если хотите сделать привычку общедоступной"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]
