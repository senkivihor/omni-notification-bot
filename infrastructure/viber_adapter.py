from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage
from core.interfaces import INotificationChannel
import logging

class ViberAdapter(INotificationChannel):
    def __init__(self, auth_token: str, name: str, avatar: str):
        self.viber = Api(BotConfiguration(name, avatar, auth_token))
        self.logger = logging.getLogger("ViberAdapter")

    def platform_name(self) -> str:
        return "viber"

    def send_message(self, user_id: str, message: str) -> bool:
        try:
            self.viber.send_messages(user_id, [TextMessage(text=message)])
            self.logger.info(f"Sent Viber message to {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Viber Error: {e}")
            return False

    def get_api_client(self):
        return self.viber
    