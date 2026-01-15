import requests
import logging
from core.interfaces import INotificationChannel

class TelegramAdapter(INotificationChannel):
    def __init__(self, bot_token: str):
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.logger = logging.getLogger("TelegramAdapter")

    def platform_name(self) -> str:
        return "telegram"

    def send_message(self, user_id: str, message: str) -> bool:
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                "chat_id": user_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            resp = requests.post(url, json=payload, timeout=5)
            
            if resp.status_code == 200:
                self.logger.info(f"Sent Telegram message to {user_id}")
                return True
            else:
                self.logger.error(f"Telegram Error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            self.logger.error(f"Telegram Exception: {e}")
            return False

    def send_welcome_button(self, chat_id: str):
        """Specific helper to ask for phone number in Telegram"""
        url = f"{self.api_url}/sendMessage"
        keyboard = {
            "keyboard": [[{
                "text": "📱 Share Phone Number",
                "request_contact": True
            }]],
            "one_time_keyboard": True,
            "resize_keyboard": True
        }
        requests.post(url, json={
            "chat_id": chat_id,
            "text": "👋 Welcome! Please share your number so we can link your orders.",
            "reply_markup": keyboard
        })
