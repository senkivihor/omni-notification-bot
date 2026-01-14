🔔 Omni-Notification Bot
A production-grade, omnichannel notification service designed to send transactional updates (e.g., "Order Ready") to clients via Telegram or Viber.

Built with Python (Flask), PostgreSQL, and Docker, following Hexagonal Architecture (Ports & Adapters) principles.

🚀 Key Features
⚡ Smart Routing Engine: Automatically decides where to send the message to save costs.

Priority 1: Telegram (100% Free, Unlimited).

Priority 2: Viber (Uses Free Bot API limits).

🔗 Deep Link Integration: No clunky QR codes. Users connect via a single click (viber:// or t.me/) which automatically links their User ID to their specific Order ID.

🛡️ Hexagonal Architecture: Business logic is completely decoupled from external frameworks (Viber/Telegram APIs), making the code testable and modular.

🐳 Dockerized: One command to spin up the App and the Database.

🔒 Secure: Internal trigger endpoints are protected by API Keys.

🛠️ Tech Stack
Language: Python 3.11

Framework: Flask

Database: PostgreSQL (via SQLAlchemy)

Containerization: Docker & Docker Compose

Testing: Pytest (with Mocking)

Libraries: viberbot, requests, psycopg2-binary, gunicorn

📂 Project Structure
Plaintext

/omni-notification-bot
├── core/                   # Domain Logic & Interfaces (Pure Python)
├── infrastructure/         # Adapters (Viber, Telegram, Database)
├── services/               # Smart Routing Logic ("The Brain")
├── tests/                  # Unit Tests (Pytest)
├── main.py                 # Application Entry Point (Webhooks)
├── docker-compose.yml      # Orchestration
└── Dockerfile              # Container definition
⚡ Getting Started
1. Prerequisites
Docker & Docker Compose installed.

Viber Bot Token: Get it from the Viber Admin Panel.

Telegram Bot Token: Get it from @BotFather.

Ngrok (For local development webhooks).

2. Configuration
Create a .env file in the root directory:

Ini, TOML

# .env
VIBER_AUTH_TOKEN=your_viber_token_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
INTERNAL_API_KEY=my_secure_internal_key
DATABASE_URL=postgresql://viber_admin:secret@db:5432/viber_bot_db
3. Run with Docker
Start the application and the database:

Bash

docker-compose up --build -d
App: Running on http://localhost:5000

DB: PostgreSQL running internally on port 5432.

🔌 Connecting the Webhooks
Since your bot runs on localhost (or a cloud server), you must tell Viber and Telegram where to send events.

1. Set Telegram Webhook:

Bash

curl "https://api.telegram.org/bot<YOUR_TELEGRAM_TOKEN>/setWebhook?url=https://your-domain.com/webhook/telegram"
2. Set Viber Webhook:

Bash

curl -X POST -H "X-Viber-Auth-Token: <YOUR_VIBER_TOKEN>" \
-d '{"url": "https://your-domain.com/webhook/viber"}' \
https://chatapi.viber.com/pa/set_webhook
📖 Usage Guide
1. The User Flow (Connecting Clients)
Instead of asking clients to "Search for the bot", use Deep Links in your Order Confirmation SMS/Email.

Telegram Link: https://t.me/YourBotName?start=ORD-1234

Viber Link: viber://pa?chatURI=YourBotName&context=ORD-1234

When the user clicks this link and taps "Start", the bot captures the ORD-1234 context and links it to their social ID in the database.

2. The Trigger Flow (Sending Notifications)
When an order is ready in your warehouse, your backend system calls the Bot's Internal API.

POST /trigger-notification Headers: X-Internal-API-Key: my_secure_internal_key Body:

JSON

{
  "phone": "+380501234567",
  "order_id": "ORD-1234",
  "items": ["Laptop", "Mouse"]
}
Response:

200 OK: {"status": "Sent via Telegram"}

200 OK: {"status": "Sent via Viber"}

200 OK: {"status": "Failed: User not found"}

🧪 Testing
The project uses pytest for unit testing. We mock all external API calls (Telegram/Viber/DB) so tests run instantly and offline.

Bash

# Run tests inside the container (if running)
docker-compose exec bot pytest

# OR run locally (requires pip install pytest)
pytest
🧠 Smart Routing Logic
The logic inside services/smart_notifier.py ensures cost efficiency:

Check Database: Look up the User by phone_number.

Try Telegram: If telegram_id exists, send message there.

Why? It is faster, free, and has no 24-hour delivery window restrictions.

Fallback to Viber: If Telegram is missing (or fails), check for viber_id.

Why? Uses the free Bot API quota (10k/month).

Failure: If neither ID exists, log the error (client hasn't subscribed yet).
