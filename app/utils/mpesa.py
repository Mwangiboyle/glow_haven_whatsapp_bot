
import os
import base64
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")
MPESA_CALLBACK_URL = os.getenv(
    "MPESA_CALLBACK_URL",
    "https://10ad98e5ed65.ngrok-free.app/api/payments/callback"
)

MPESA_BASE_URL = (
    "https://sandbox.safaricom.co.ke"
    if MPESA_ENV == "sandbox"
    else "https://api.safaricom.co.ke"
)


async def get_access_token() -> str:
    """
    Generate OAuth access token for M-Pesa Daraja API (async)
    """
    url = f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=aiohttp.BasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("access_token")
            text = await response.text()
            raise Exception(f"❌ Failed to get access token: {text}")


def generate_password(shortcode: str, passkey: str, timestamp: str) -> str:
    """
    Generate Base64 password for STK Push
    """
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


async def initiate_stk_push(payment) -> dict:
    """
    Trigger M-Pesa STK Push
    """
    access_token = await get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = generate_password(MPESA_SHORTCODE, MPESA_PASSKEY, timestamp)

    stk_url = f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": payment.amount,
        "PartyA": payment.phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": payment.phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": f"Booking-{payment.booking_id}",
        "TransactionDesc": "Glow Haven Beauty Lounge Booking Payment"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(stk_url, json=payload, headers=headers) as response:
            resp_data = await response.json()
            print(f"📤 STK Push ({response.status}): {resp_data}")
            return resp_data
