from datetime import timedelta

from celery import shared_task
from .services import send_telegram_message
from .models import Habbit
from django.utils import timezone


@shared_task
def send_notices():
    now = timezone.now()
    # Окно в 1 минуту для проверки времени
    time_window_start = now - timedelta(seconds=30)
    time_window_end = now + timedelta(seconds=30)

    # Получаем привычки, которые должны быть выполнены в текущий момент
    habits = Habbit.objects.filter(
        time__gte=time_window_start,
        time__lte=time_window_end,
    )

    for habit in habits:
        # Проверяем, подходит ли текущий день с учетом периодичности
        created_at = habit.created_at
        days_since_creation = (now.date() - created_at.date()).days
        if days_since_creation % habit.periodicity_days == 0:
            chat_id = habit.user.telegram_id
            message = f"Просили напомнить о привычке {habit.action} в {habit.place}."
            send_telegram_message(chat_id=chat_id, message=message)
