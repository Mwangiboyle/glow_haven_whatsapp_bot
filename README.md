# Glow Haven Beauty Lounge – WhatsApp AI Assistant + FastAPI Backend

A FastAPI backend with a WhatsApp chatbot that helps users:

- Create and check bookings  
- Optionally initiate M-Pesa STK push and auto-send PDF receipts  
- Persist short-term chat memory per WhatsApp user  
- Expose MCP tools the LLM can call to interact with your API  
- Optional Google Calendar sync for bookings  

## Features
- **Booking API:** create/list/get bookings  
- **WhatsApp webhook (Twilio):** async bot with MCP tool calls  
- **Payments (optional):** STK push, status polling, receipt generation, WhatsApp notification  
- **Google Calendar (optional):** auto-create and backfill events  
- **Developer-friendly:** auto table creation on startup  

## Tech Stack
FastAPI, SQLAlchemy, SQLite (dev), Twilio WhatsApp, OpenAI (chat + tools), MCP tools (HTTP client), ReportLab (PDF), Optional Google Calendar API

## Project Structure
```
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── api/
│   ├── bookings.py
│   ├── services.py
│   ├── payments.py
│   ├── receipts.py
│   └── feedback.py
├── whatsapp/
│   ├── webhook.py
│   ├── bot.py
│   ├── client.py
│   └── memory.py
├── mcp_server/
│   └── tools.py
└── utils/
    ├── mpesa.py
    └── pdf_generator.py
```

## Getting Started

### 1) Requirements
- Python 3.11+  
- Twilio account (for WhatsApp)  
- OpenAI API key  
- Optional: M-Pesa Daraja credentials, Google Calendar credentials  

### 2) Installation
```bash
pip install -r requirements.txt
```

If missing, create a `requirements.txt` with:
```
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
```

### 3) Environment Variables
Create a `.env` file in your project root:
```
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
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google_cred.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CALENDAR_TIMEZONE=Africa/Nairobi
```

### 4) Run Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000
```

Docs: [http://localhost:9000/docs](http://localhost:9000/docs)

### 5) Configure Twilio Webhook
Set webhook URL in Twilio console to:  
`POST https://your-domain/whatsapp/webhook`

In dev, use ngrok to tunnel your localhost.

---

## API Overview
Base path: `/api`

### Services
- `GET /api/services/`
- `GET /api/services/list`

### Bookings
- `POST /api/bookings/create`
- `GET /api/bookings/list`
- `GET /api/bookings/{booking_id}`
- `POST /api/bookings/sync_calendar` *(optional)*

### Payments (optional)
- `POST /api/payments/stkpush`
- `GET /api/payments/status/{booking_id}`
- `POST /api/payments/callback`

### Receipts
- `POST /api/receipts/generate/{booking_id}`

### WhatsApp Webhook
- `POST /whatsapp/webhook`

---

## WhatsApp Bot Behavior
`chat_with_bot` in `whatsapp/bot.py` handles user sessions:  
- Maintains per-user memory  
- Uses OpenAI to call MCP tools  
- System prompt guides conversation flow  

---

## MCP Tools
Defined in `mcp_server/tools.py`, includes:
- `get_services`
- `get_business_info`
- `get_user_bookings`
- `create_booking`
- `initiate_payment`
- `poll_payment_status`
- `generate_receipt`
- `submit_feedback`


