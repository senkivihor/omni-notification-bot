import pytest
from core.models import UserDTO

# Pytest automatically injects the 'service', 'mock_deps', and 'dummy_user' fixtures
# defined in conftest.py

def test_notify_uses_telegram_first_if_user_has_both(service, mock_deps, dummy_user):
    # --- ARRANGE ---
    # Setup the repository to return our dummy user (who has both IDs)
    mock_deps["repo"].get_user_by_phone.return_value = dummy_user
    # Ensure Telegram succeeds
    mock_deps["telegram"].send_message.return_value = True

    # --- ACT ---
    result = service.notify_order_ready("+12345", "ORD-1", ["Item"])

    # --- ASSERT ---
    # 1. Telegram should be called
    mock_deps["telegram"].send_message.assert_called_once()
    assert "tg_999" in mock_deps["telegram"].send_message.call_args[0]
    
    # 2. Viber should NOT be called (Cost saving logic)
    mock_deps["viber"].send_message.assert_not_called()
    
    # 3. Check return string
    assert result == "Sent via Telegram"

def test_notify_falls_back_to_viber_if_user_only_has_viber(service, mock_deps):
    # --- ARRANGE ---
    # Create a specific user for this test (Viber only)
    user_viber_only = UserDTO("+123", "Bob", viber_id="vib_1", telegram_id=None)
    mock_deps["repo"].get_user_by_phone.return_value = user_viber_only
    
    mock_deps["viber"].send_message.return_value = True

    # --- ACT ---
    result = service.notify_order_ready("+123", "ORD-1", ["Item"])

    # --- ASSERT ---
    mock_deps["telegram"].send_message.assert_not_called()
    mock_deps["viber"].send_message.assert_called_once()
    assert result == "Sent via Viber"

def test_notify_falls_back_to_viber_if_telegram_fails(service, mock_deps, dummy_user):
    # --- ARRANGE ---
    mock_deps["repo"].get_user_by_phone.return_value = dummy_user
    
    # Telegram fails (returns False)
    mock_deps["telegram"].send_message.return_value = False
    # Viber succeeds
    mock_deps["viber"].send_message.return_value = True

    # --- ACT ---
    service.notify_order_ready("+123", "ORD-1", ["Item"])

    # --- ASSERT ---
    # Both should have been tried
    mock_deps["telegram"].send_message.assert_called_once()
    mock_deps["viber"].send_message.assert_called_once()

def test_notify_handles_user_not_found(service, mock_deps):
    # --- ARRANGE ---
    mock_deps["repo"].get_user_by_phone.return_value = None

    # --- ACT ---
    result = service.notify_order_ready("+000", "ORD", [])

    # --- ASSERT ---
    assert "User not found" in result
    mock_deps["telegram"].send_message.assert_not_called()
