
# whatsapp/client.py
import os
from dotenv import load_dotenv
from twilio.rest import Client
import asyncio
from typing import Optional

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

_twilio_client: Optional[Client] = None


def _get_twilio_client() -> Client:
    global _twilio_client
    if _twilio_client is None:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            raise RuntimeError("Twilio credentials are not set in environment variables.")
        _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return _twilio_client


def send_whatsapp_message_sync(to: str, body: str) -> str:
    """
    Synchronous helper using Twilio SDK.
    `to` should be in international format (e.g. "+254712345678") or "whatsapp:+..."
    Returns message SID on success.
    """
    client = _get_twilio_client()
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"
    msg = client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=body, to=to)
    return msg.sid


async def send_whatsapp_message(to: str, body: str) -> str:
    """
    Async wrapper around the synchronous Twilio send function.
    Safe to call from async code.
    """
    loop = asyncio.get_running_loop()
    sid = await loop.run_in_executor(None, send_whatsapp_message_sync, to, body)
    return sid

