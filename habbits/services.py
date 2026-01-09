import requests
from config.settings import TELEGRAM_BOT_TOKEN

BOT_TOKEN = TELEGRAM_BOT_TOKEN


def send_telegram_message(chat_id, message):
    params = {"text": message, "chat_id": chat_id}

    requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params=params)
