
# whatsapp/webhook.py
import asyncio
from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse
from whatsapp.client import send_whatsapp_message
from whatsapp.bot import chat_with_bot  # your async function from bot.py
import logging

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

logger = logging.getLogger("whatsapp_webhook")
logging.basicConfig(level=logging.INFO)


@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
):
    """
    Twilio WhatsApp webhook endpoint.
    Twilio sends form-encoded fields including 'From' and 'Body'.
    We schedule the processing asynchronously and return quickly.
    """
    try:
        user_number = From.replace("whatsapp:", "").strip()
        user_message = Body.strip()

        logger.info("Incoming message from %s: %s", user_number, user_message)

        # Schedule processing in the event loop (non-blocking for Twilio)
        asyncio.create_task(_process_and_reply(user_number, user_message))

        # Immediately acknowledge to Twilio
        return PlainTextResponse("OK", status_code=200)

    except Exception as e:
        logger.exception("Webhook error")
        return PlainTextResponse("ERROR", status_code=500)


async def _process_and_reply(user_number: str, user_message: str):
    """
    Coroutine that calls your bot, then sends reply via Twilio.
    Runs in background (scheduled with create_task).
    """
    try:
        # Get bot reply (calls MCP + OpenAI via your bot.chat_with_bot)
        bot_reply = await chat_with_bot(user_message)

        if not bot_reply:
            bot_reply = "Sorry, I couldn't process your request right now. Please try again."

        # Send WhatsApp message (async wrapper)
        sid = await send_whatsapp_message(user_number, bot_reply)
        logger.info("Replied to %s, message SID: %s", user_number, sid)

    except Exception as e:
        # Log the error; avoid crashing the event loop
        logger.exception("Error processing message for %s", user_number)

