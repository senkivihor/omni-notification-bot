# main.py
import os
import logging
from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberMessageRequest, ViberConversationStartedRequest
from viberbot.api.messages import ContactMessage

# Import our hexagonal layers
# Ensure you have your folders: core/, infrastructure/, services/
from infrastructure.database import init_db
from infrastructure.repositories import SqlAlchemyUserRepository
from infrastructure.viber_adapter import ViberAdapter
from infrastructure.telegram_adapter import TelegramAdapter
from services.smart_notifier import SmartNotificationService

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OmniBot")

app = Flask(__name__)

# --- CONFIGURATION (Loaded from Env for Security) ---
VIBER_TOKEN = os.getenv("VIBER_AUTH_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INTERNAL_KEY = os.getenv("INTERNAL_API_KEY")

# --- INITIALIZATION ---
# 1. Database
init_db()
repo = SqlAlchemyUserRepository()

# 2. Adapters
viber_adapter = ViberAdapter(VIBER_TOKEN, "OmniShopBot", "http://site.com/avatar.jpg")
telegram_adapter = TelegramAdapter(TELEGRAM_TOKEN)

# 3. Service (The Brain)
notifier = SmartNotificationService(viber_adapter, telegram_adapter, repo)


# ==========================
# 1. VIBER WEBHOOK
# ==========================
@app.route('/webhook/viber', methods=['POST'])
def viber_webhook():
    viber = viber_adapter.get_api_client()
    # Verify Signature (Security)
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    # Case A: User clicked a Deep Link (viber://...&context=ORD-123)
    if isinstance(viber_request, ViberConversationStartedRequest):
        user_id = viber_request.user.id
        context = viber_request.context  # "ORD-123"

        if context and context.startswith("ORD-"):
            # TODO: Add logic to link user_id to this Order ID immediately
            logger.info(f"🔗 Deep Link: User {user_id} connected via Context {context}")
            # Note: In conversation_started, we must return the message in the response, not send it
            # For simplicity here, we just return OK. Real app should return a welcome message JSON.

    # Case B: User shared Contact Info
    elif isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        user_id = viber_request.sender.id
        
        if isinstance(message, ContactMessage):
            phone = message.contact.phone_number
            name = message.contact.name
            logger.info(f"captured Viber contact: {phone}")
            
            repo.save_or_update_user(phone=phone, name=name, viber_id=user_id)
            viber_adapter.send_message(user_id, "✅ Connected! You will receive updates here.")

    return Response(status=200)


# ==========================
# 2. TELEGRAM WEBHOOK
# ==========================
@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    data = request.json
    
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        
        # User clicked "Start" -> Ask for Phone
        if "text" in msg and msg["text"].startswith("/start"):
            # If deep link used: /start ORD-123
            args = msg["text"].split()
            if len(args) > 1:
                context = args[1]
                logger.info(f"🔗 Telegram Deep Link context: {context}")
            
            telegram_adapter.send_welcome_button(chat_id)

        # User clicked "Share Phone"
        elif "contact" in msg:
            contact = msg["contact"]
            phone = contact["phone_number"]
            # Telegram sometimes sends numbers without '+'. Fix it.
            if not phone.startswith('+'): 
                phone = '+' + phone
                
            name = contact.get("first_name", "Client")
            
            repo.save_or_update_user(phone=phone, name=name, telegram_id=str(chat_id))
            telegram_adapter.send_message(chat_id, "✅ Connected! You will receive updates here.")

    return Response("OK", status=200)


# ==========================
# 3. INTERNAL TRIGGER API
# ==========================
@app.route('/trigger-notification', methods=['POST'])
def trigger():
    # Security Check
    key = request.headers.get("X-Internal-API-Key")
    if key != INTERNAL_KEY:
        return Response("Unauthorized", status=403)

    data = request.json
    # Expects: { "phone": "+123...", "order_id": "123", "items": ["A", "B"] }
    
    if not data or 'phone' not in data:
        return Response("Missing 'phone' in payload", status=400)

    result = notifier.notify_order_ready(
        phone_number=data['phone'],
        order_id=data.get('order_id', 'Unknown'),
        items=data.get('items', [])
    )
    
    logger.info(f"Trigger Result: {result}")
    return {"status": result}, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)