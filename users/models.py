from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.CharField(
        max_length=100, unique=True, help_text="Введите свой chat id"
    )

    REQUIRED_FIELDS = []