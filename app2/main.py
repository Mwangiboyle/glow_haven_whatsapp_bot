from fastapi import FastAPI, HTTPException, Request
from .api.utils import check_service, calculate_payment, initiate_payment, poll_payment_status
from .api.utils import router as daraja_router, generate_receipt, add_booking_to_db
from .api.google_calendar import add_to_calendar
from typing import Optional
from pydantic import BaseModel

class BookingRequest(BaseModel):
    customer_name: str
    phone_number: str
    service_name: str
    date: str  # or use datetime.date
    time: str  # or use datetime.time
    amount: Optional[float] = None
app = FastAPI()

app.include_router(daraja_router, prefix="/daraja")


@app.post("/bookings/full_flow")
async def booking_full_flow(request: BookingRequest):
    customer_name = request.customer_name
    phone_number = request.phone_number
    service_name = request.service_name
    date = request.date
    time = request.time

    status = {}

    # 1️⃣ Check service exists
    service_ok = await check_service(service_name)
    if not service_ok:
        status["service_check"] = "failed"
        raise HTTPException(status_code=400, detail="Service not found")
    status["service_check"] = "success"

    # 2️⃣ Calculate deposit
    amount = await calculate_payment(service_name)
    status["payment_amount"] = amount


    payment = await initiate_payment(phone_number, amount)
    if not payment["id"]:
        raise HTTPException(status_code=400, detail="Payment initiation failed")

    status = {"payment": "pending"}

    # 2️⃣ Poll payment status until callback updates the DB
    payment_status = await poll_payment_status(payment["id"])
    if payment_status != "success":
        status["payment"] = "failed"
        raise HTTPException(status_code=400, detail="Payment failed or timed out")

    status["payment"] = "success"

   # 5️⃣ Generate receipt
    receipt_path = await generate_receipt(payment["id"], customer_name, service_name)
    status["receipt"] = "success"

    # 6️⃣ Add booking to DB
    booking = await add_booking_to_db(customer_name, phone_number, service_name, date, time, amount)
    status["db"] = "success"

     # 7️⃣ Add to Google Calendar
    calendar_link = await add_to_calendar(customer_name, date, time, service_name)
    status["calendar"] = "success"

    # 8️⃣ Return results
    return {
        "message": "Booking complete",
        "booking": booking,
        "payment": payment,
        "receipt_path": receipt_path,
        "calendar_link": calendar_link,
        "status": status,
        "next_step": "Please provide feedback"
    }
