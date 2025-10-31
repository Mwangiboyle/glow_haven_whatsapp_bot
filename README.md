Glow Haven Beauty Lounge – WhatsApp AI Assistant + FastAPI Backend

A FastAPI backend integrated with a WhatsApp chatbot that helps Glow Haven Beauty Lounge customers seamlessly book appointments, make payments, and receive receipts — powered by OpenAI, Twilio, and MCP tools.

✨ Features

💬 WhatsApp Chatbot (Twilio + OpenAI)

Handles customer queries, bookings, and feedback

Maintains short-term chat memory per user

Calls FastAPI endpoints through MCP tools

📅 Booking API

Create, list, and retrieve bookings

Optional Google Calendar sync

💰 Payment Integration (Optional)

M-Pesa STK Push initiation

Payment status polling and receipts

Auto WhatsApp receipt notification

🧾 PDF Receipt Generation

Automatically created and stored upon successful payment

🧠 LLM Tooling

The OpenAI model uses MCP tools to call your FastAPI endpoints

🔧 Dev-Friendly

Tables auto-created on startup

Optional integrations (Google Calendar, M-Pesa) can be disabled in dev

🧱 Tech Stack
Category	Tools
Backend	FastAPI, SQLAlchemy, SQLite
Messaging	Twilio WhatsApp API
AI/LLM	OpenAI GPT (via chat_with_bot)
Automation	MCP Tools
Documents	ReportLab (PDF)
Optional	Google Calendar API, M-Pesa Daraja
📂 Project Structure
app/
├── main.py
├── database.py
├── models.py          # SQLAlchemy models
├── schemas.py         # Pydantic I/O models
│
├── api/
│   ├── bookings.py
│   ├── services.py
│   ├── payments.py
│   ├── receipts.py
│   └── feedback.py
│
├── whatsapp/
│   ├── webhook.py
│   ├── bot.py
│   ├── client.py
│   └── memory.py      # (for chat memory)
│
├── mcp_server/
│   └── tools.py
│
└── utils/
    ├── mpesa.py
    └── pdf_generator.py

🚀 Getting Started
1️⃣ Requirements

Python 3.11+

Virtual environment or Docker

Twilio account (for WhatsApp)

OpenAI API key

(Optional) M-Pesa Daraja credentials

(Optional) Google service account credentials for Calendar

2️⃣ Installation
# Create and activate venv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


If missing, create a requirements.txt similar to:

fastapi
uvicorn[standard]
sqlalchemy
python-dotenv
pydantic
httpx
openai
mcp
reportlab
google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib

3️⃣ Environment Variables

Create a .env file in the project root:

OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///./glow_haven.db
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
API_BASE_URL=http://localhost:9000/api

# Optional M-Pesa
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
MPESA_SHORTCODE=...
MPESA_PASSKEY=...
MPESA_CALLBACK_URL=https://your-public-domain/api/payments/callback

# Optional Google Calendar
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/google_cred.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CALENDAR_TIMEZONE=Africa/Nairobi

4️⃣ Run Locally
uvicorn app.main:app --host 0.0.0.0 --port 9000


Docs: http://localhost:9000/docs

Health: http://localhost:9000/

Tables are auto-created on startup.

5️⃣ Configure Twilio WhatsApp Webhook

Set your webhook URL:

POST https://<your-public-domain>/whatsapp/webhook


Twilio sends:

From

Body

In development, expose your server via ngrok and configure the webhook in your Twilio sandbox.

🔌 API Overview

Base Path: /api

📋 Services
GET /api/services/
GET /api/services/list

📅 Bookings
POST /api/bookings/create
GET /api/bookings/list
GET /api/bookings/{booking_id}
POST /api/bookings/sync_calendar   # optional

💰 Payments (optional)
POST /api/payments/stkpush
GET /api/payments/status/{booking_id}
POST /api/payments/callback


On success, generates a PDF receipt and sends WhatsApp confirmation.

🧾 Receipts
POST /api/receipts/generate/{booking_id}

💬 WhatsApp Webhook
POST /whatsapp/webhook

🤖 WhatsApp Bot Behavior

Implemented in whatsapp/bot.py:

Maintains per-user memory (via memory.py)

Uses OpenAI LLM + MCP tools

Calculates 30% deposit for bookings

Calls tools like:

create_booking

initiate_payment

generate_receipt

🛠 MCP Tools

Defined in mcp_server/tools.py — the bridge between LLM and backend APIs.

Example tools:

get_services

create_booking

initiate_payment

generate_receipt

submit_feedback

Set API_BASE_URL in .env so MCP knows where to call your backend.

💳 Payment Flow (Optional)

User confirms booking.

Bot calculates 30% deposit.

Bot calls initiate_payment.

M-Pesa sends STK Push.

On callback success:

Booking → marked as paid

Receipt → generated (PDF)

WhatsApp → confirmation sent

🗓 Google Calendar Integration (Optional)

Auto-adds bookings as calendar events.

Backfill missing ones via:

POST /api/bookings/sync_calendar


To grant access:

Share your calendar with the service account email.

Permission: “Make changes to events.”

⚙️ Deployment

You can deploy via:

Render (Dockerized build)

Railway

Docker Hub + Render combo

Example build command:

docker build -t glow-haven:latest .
docker run -p 9000:9000 glow-haven

🧩 Future Improvements

Add secure user authentication for admin panel

Connect to live M-Pesa STK Push

Enable persistent memory via Redis or Supabase

Add email/SMS notifications for confirmed bookings

Fine-tune conversation flow with WhatsApp interactive buttons
