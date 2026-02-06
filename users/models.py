from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None # models.CharField(max_length=50, verbose_name="Пользователь", blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    password = models.CharField(max_length=100, verbose_name='Пароль пользователя')
    telegram_id = models.CharField(
        max_length=100, unique=True, help_text="Введите свой chat id"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    def __str__(self):
        return f'{self.username}'


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'