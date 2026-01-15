import pytest
from unittest.mock import MagicMock
from core.models import UserDTO
from services.smart_notifier import SmartNotificationService

@pytest.fixture
def mock_deps():
    """
    Creates fresh mocks for every single test.
    Returns a dictionary or object containing all mocks.
    """
    return {
        "viber": MagicMock(),
        "telegram": MagicMock(),
        "repo": MagicMock()
    }

@pytest.fixture
def service(mock_deps):
    """
    Automatically injects the mocks into the Service.
    """
    return SmartNotificationService(
        viber=mock_deps["viber"],
        telegram=mock_deps["telegram"],
        repo=mock_deps["repo"]
    )

@pytest.fixture
def dummy_user():
    """Returns a basic user object to save typing."""
    return UserDTO(
        phone_number="+1234567890",
        name="Test User",
        viber_id="viber_123",
        telegram_id="tg_999"
    )
