from dataclasses import dataclass
from typing import Optional

@dataclass
class UserDTO:
    phone_number: str
    name: str
    viber_id: Optional[str] = None
    telegram_id: Optional[str] = None
