import pytest
from unittest.mock import patch, MagicMock
from infrastructure.telegram_adapter import TelegramAdapter
from infrastructure.viber_adapter import ViberAdapter

# --- TELEGRAM TESTS ---

def test_telegram_send_message_success():
    adapter = TelegramAdapter("fake_token")
    
    # --- ARRANGE ---
    # We patch 'requests.post' so we don't hit the real internet
    with patch("infrastructure.telegram_adapter.requests.post") as mock_post:
        # Mock a successful 200 OK response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # --- ACT ---
        result = adapter.send_message("123", "Hello")

        # --- ASSERT ---
        assert result is True
        mock_post.assert_called_once()
        # Verify correct URL construction
        assert "https://api.telegram.org/botfake_token/sendMessage" in mock_post.call_args[0][0]

def test_telegram_send_message_failure():
    adapter = TelegramAdapter("fake_token")

    with patch("infrastructure.telegram_adapter.requests.post") as mock_post:
        # --- ARRANGE ---
        # Mock a 400 Bad Request
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        # --- ACT ---
        result = adapter.send_message("123", "Hello")

        # --- ASSERT ---
        assert result is False


# --- VIBER TESTS ---

def test_viber_send_message_calls_library():
    # --- ARRANGE ---
    # Patch the 'Api' class inside the viber adapter file
    with patch("infrastructure.viber_adapter.Api") as MockApi:
        mock_viber_instance = MockApi.return_value
        adapter = ViberAdapter("token", "Bot", "avatar")

        # --- ACT ---
        adapter.send_message("user_viber_1", "Hello")

        # --- ASSERT ---
        mock_viber_instance.send_messages.assert_called_once()
        args = mock_viber_instance.send_messages.call_args
        
        # Check first argument (User ID)
        assert args[0][0] == "user_viber_1"
        # Check second argument (Message Text)
        assert args[0][1][0].text == "Hello"

def test_viber_handles_exceptions():
    with patch("infrastructure.viber_adapter.Api") as MockApi:
        # --- ARRANGE ---
        mock_viber_instance = MockApi.return_value
        # Simulate library crashing
        mock_viber_instance.send_messages.side_effect = Exception("Connection Error")
        
        adapter = ViberAdapter("token", "Bot", "avatar")

        # --- ACT ---
        result = adapter.send_message("user_1", "Hi")

        # --- ASSERT ---
        assert result is False
        