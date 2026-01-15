from infrastructure.database import UserORM, SessionLocal
from core.interfaces import IUserRepository
from core.models import UserDTO

class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self):
        self._session_factory = SessionLocal

    def save_or_update_user(self, phone: str, name: str, viber_id: str = None, telegram_id: str = None) -> None:
        with self._session_factory() as session:
            user = session.query(UserORM).filter_by(phone_number=phone).first()
            
            if user:
                # Update existing user info
                user.name = name
                if viber_id: user.viber_id = viber_id
                if telegram_id: user.telegram_id = telegram_id
            else:
                # Create new user
                new_user = UserORM(
                    phone_number=phone, 
                    name=name, 
                    viber_id=viber_id, 
                    telegram_id=telegram_id
                )
                session.add(new_user)
            
            session.commit()

    def get_user_by_phone(self, phone: str) -> UserDTO | None:
        with self._session_factory() as session:
            user = session.query(UserORM).filter_by(phone_number=phone).first()
            if user:
                return UserDTO(
                    phone_number=user.phone_number,
                    name=user.name,
                    viber_id=user.viber_id,
                    telegram_id=user.telegram_id
                )
            return None
