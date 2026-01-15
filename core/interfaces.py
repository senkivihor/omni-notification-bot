from abc import ABC, abstractmethod

class INotificationChannel(ABC):
    @abstractmethod
    def send_message(self, user_id: str, message: str) -> bool:
        """Sends a text message to the platform-specific ID."""
        pass
    
    @abstractmethod
    def platform_name(self) -> str:
        """Returns 'viber' or 'telegram'."""
        pass

class IUserRepository(ABC):
    @abstractmethod
    def save_or_update_user(self, phone: str, name: str, viber_id: str = None, telegram_id: str = None) -> None:
        pass

    @abstractmethod
    def get_user_by_phone(self, phone: str):
        pass