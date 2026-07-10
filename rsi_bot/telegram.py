from __future__ import annotations

import json
import os
from typing import Any

import requests


class TelegramNotifier:
    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, message: str) -> bool:
        if not self.is_configured():
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
        }
        response = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            data=payload,
            timeout=10,
        )
        return response.ok
