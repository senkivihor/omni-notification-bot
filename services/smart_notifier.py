from core.interfaces import INotificationChannel, IUserRepository

class SmartNotificationService:
    def __init__(self, 
                 viber: INotificationChannel, 
                 telegram: INotificationChannel, 
                 repo: IUserRepository):
        self.viber = viber
        self.telegram = telegram
        self.repo = repo

    def notify_order_ready(self, phone_number: str, order_id: str, items: list) -> str:
        # 1. Look up user
        user = self.repo.get_user_by_phone(phone_number)
        
        if not user:
            return "User not found in database."

        message = (
            f"📦 *Order #{order_id} Ready!*\n"
            f"Items: {', '.join(items)}\n"
            "📍 Come pick it up!"
        )

        # 2. PRIORITY LOGIC: Try Telegram first (Better UX/Free)
        if user.telegram_id:
            print(f"🚀 Sending via Telegram to {user.name}...")
            if self.telegram.send_message(user.telegram_id, message):
                return "Sent via Telegram"
        
        # 3. FALLBACK LOGIC: Try Viber
        if user.viber_id:
            print(f"🚀 Sending via Viber to {user.name}...")
            if self.viber.send_message(user.viber_id, message):
                return "Sent via Viber"

        return "Failed: User exists but has no active messaging channels."
