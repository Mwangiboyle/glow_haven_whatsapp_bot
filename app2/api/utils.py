import json
import httpx
import os
from datetime import datetime, timezone
from base64 import b64encode
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime
import os

MONGO_URI = "mongodb://localhost:27017"  # or your cloud URI
DB_NAME = "glowhaven"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
payments_collection = db["payments"]
bookings_collection = db["bookings"]
load_dotenv()


payments = {}

async def check_service(service_name: str) -> bool:
    """
    Check if a service exists in the services.json file.

    :param service_name: Name of the service to check
    :return: True if service exists, False otherwise
    """
    # Load the JSON data from a file
    with open("business.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Search for the service
    for category in data.get("services", []):
        for item in category.get("items", []):
            if item.get("name", "").lower() == service_name.lower():
                return True
    return False


async def calculate_payment(service_name: str) -> float:
    """
    Calculate 30% deposit for a given service.

    :param service_name: Name of the service
    :return: 30% of the service price
    :raises ValueError: If service not found
    """
    # Load the JSON data
    with open("business.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Search for the service
    for category in data.get("services", []):
        for item in category.get("items", []):
            if item.get("name", "").lower() == service_name.lower():
                price = item.get("price", 0)
                return round(price * 0.3, 2)  # 30% deposit, rounded to 2 decimals

    raise ValueError(f"Service '{service_name}' not found.")




DARAJA_BASE_URL = "https://sandbox.safaricom.co.ke"
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
BUSINESS_SHORT_CODE = os.getenv("DARJA_SHORTCODE", "174379")
PASSKEY = os.getenv("MPESA_PASSKEY")
CALLBACK_URL = "https://195404c71073.ngrok-free.app/daraja/callback"

async def get_access_token():
    auth = (CONSUMER_KEY, CONSUMER_SECRET)
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{DARAJA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            auth=auth,
        )
        res.raise_for_status()
        return res.json()["access_token"]


async def initiate_payment(phone_number: str, amount: float):
    access_token = await get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    import base64
    password = base64.b64encode(f"{BUSINESS_SHORT_CODE}{PASSKEY}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": BUSINESS_SHORT_CODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Glow Haven Beauty Lounge",
        "TransactionDesc": "Booking deposit",
    }

    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        res = await client.post(f"{DARAJA_BASE_URL}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        res.raise_for_status()
        data = res.json()

    checkout_id = data.get("CheckoutRequestID")


# ✅ Save pending record to MongoDB
    if checkout_id:
        await payments_collection.insert_one({
            "checkout_request_id": checkout_id,
            "phone": phone_number,
            "amount": amount,
            "status": "pending",
            "created_at": datetime.now(timezone.utc)
        })


    return {"id": checkout_id, "raw": data}


async def poll_payment_status(checkout_request_id: str, timeout: int = 60):
    """Poll MongoDB until payment is success/failed or timeout."""
    for _ in range(timeout // 5):
        payment = await payments_collection.find_one({"checkout_request_id": checkout_request_id})
        if payment:
            status = payment.get("status")
            if status == "success":
                return "success"
            elif status == "failed":
                return "failed"
        await asyncio.sleep(5)
    return "pending"

async def save_callback_data(data: dict):
    try:
        callback = data["Body"]["stkCallback"]
        checkout_request_id = callback["CheckoutRequestID"]
        result_code = callback["ResultCode"]

        if result_code != 0:
            print("❌ Payment failed:", callback["ResultDesc"])
            await payments_collection.insert_one({
                "checkout_request_id": checkout_request_id,
                "status": "failed",
                "reason": callback["ResultDesc"],
                "timestamp": datetime.now(timezone.utc)
            })
            return

        metadata = {item["Name"]: item.get("Value") for item in callback["CallbackMetadata"]["Item"]}
        amount = metadata.get("Amount")
        receipt_number = metadata.get("MpesaReceiptNumber")
        transaction_date = metadata.get("TransactionDate")
        phone = metadata.get("PhoneNumber")

        payment_info = {
            "checkout_request_id": checkout_request_id,
            "amount": amount,
            "receipt_number": receipt_number,
            "transaction_date": transaction_date,
            "phone": phone,
            "status": "success",
            "created_at": datetime.now(timezone.utc)
        }

        await payments_collection.update_one(
            {"checkout_request_id": checkout_request_id},
            {"$set": payment_info},
            upsert=True
        )

        print(f" Payment saved: {receipt_number}, Amount: {amount}, Phone: {phone}")
        return payment_info

    except Exception as e:
        print("Error saving callback:", e)


async def generate_receipt(checkout_request_id: str, customer_name: str, service_name: str) -> str:
    """
    Generate a styled PDF receipt for a completed payment.
    Fetches payment info from MongoDB using checkout_request_id.
    """

    # 1️⃣ Fetch payment record from MongoDB
    payment = await payments_collection.find_one({"checkout_request_id": checkout_request_id})

    if not payment:
        raise ValueError(f"No payment found for ID: {checkout_request_id}")

    # 2️⃣ Extract the data you need safely
    phone = payment.get("phone", "N/A")
    amount = float(payment.get("amount", 0))
    mpesa_receipt = payment.get("receipt_number", "N/A")
    transaction_date = payment.get("created_at")

    # 3️⃣ Create receipts folder
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/receipt_{checkout_request_id}.pdf"

    # 4️⃣ Create PDF
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # ----- HEADER -----
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, "Glow Haven Beauty Lounge")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 70, "Payment Receipt")

    c.line(30, height - 80, width - 30, height - 80)

    # ----- PAYMENT DETAILS -----
    c.setFont("Helvetica-Bold", 12)
    y = height - 120
    c.drawString(40, y, "Receipt Details:")
    y -= 20

    # Table-like layout
    c.setFont("Helvetica", 11)
    details = [
        ("Date:", transaction_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Customer Name:", customer_name),
        ("Phone Number:", phone),
        ("Service:", service_name),
        ("Amount Paid:", f"KES {amount:.2f}"),
        ("M-Pesa Receipt Number:", mpesa_receipt),
        ("Checkout Request ID:", checkout_request_id),
    ]

    for label, value in details:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, label)
        c.setFont("Helvetica", 11)
        c.drawString(180, y, str(value))
        y -= 20

    # ----- FOOTER -----
    c.line(30, 100, width - 30, 100)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, 80, "Thank you for choosing Glow Haven Beauty Lounge!")
    c.drawCentredString(width / 2, 65, "For inquiries: info@glowhavenbeauty.co.ke | +254 712 345 678")

    # 5️⃣ Save PDF
    c.showPage()
    c.save()

    return filename


async def add_booking_to_db(customer_name: str, phone: str, service: str, date: str, time: str, amount: float):
    """
    Add a new booking document to the MongoDB 'bookings' collection.

    :param customer_name: Name of the customer
    :param phone: Customer phone number
    :param service: Service name (e.g. 'Gel Manicure')
    :param date: Booking date (YYYY-MM-DD)
    :param time: Booking time (HH:MM)
    :param amount: Service cost
    :return: The inserted document (with MongoDB _id)
    """
    booking_doc = {
        "customer_name": customer_name,
        "phone": phone,
        "service": service,
        "date": date,
        "time": time,
        "amount": amount,
        "status": "booked",
        "created_at": datetime.now(timezone.utc)
    }

    result = await bookings_collection.insert_one(booking_doc)
    booking_doc["_id"] = str(result.inserted_id)
    return booking_doc


from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/callback")
async def daraja_callback(request: Request):
    data = await request.json()
    await save_callback_data(data)
    callback = data["Body"]["stkCallback"]

    checkout_id = callback["CheckoutRequestID"]
    result_code = callback["ResultCode"]

    new_status = "success" if result_code == 0 else "failed"

    # Update the document in MongoDB
    update_result = await payments_collection.update_one(
        {"checkout_request_id": checkout_id},
        {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}}
    )
    if update_result.modified_count == 0:
        return {"ResultCode": 1, "ResultDesc": f"No payment found for {checkout_id}"}

    return {"ResultCode": 0, "ResultDesc": "Accepted"}


