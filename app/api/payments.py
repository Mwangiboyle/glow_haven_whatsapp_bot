
# app/api/payments.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Payment, Booking
from app.models import PaymentCreate, PaymentResponse
from app.utils.mpesa import initiate_stk_push
from datetime import datetime

router = APIRouter(prefix="/api/payments", tags=["Payments"])

@router.post("/stkpush", response_model=PaymentResponse)
async def stk_push(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == payment_data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    payment = Payment(
        booking_id=booking.id,
        phone_number=payment_data.phone_number,
        amount=payment_data.amount,
        status="initiated"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # trigger STK push via Daraja API
    stk_response = await initiate_stk_push(payment)

    if stk_response.get("ResponseCode") == "0":
        payment.status = "pending"
    else:
        payment.status = "failed"

    db.commit()
    db.refresh(payment)
    return payment


@router.post("/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    # Parse callback
    body = data.get("Body", {}).get("stkCallback", {})
    result_code = body.get("ResultCode")
    metadata = body.get("CallbackMetadata", {}).get("Item", [])
    transaction_id = None
    amount = None
    phone = None

    for item in metadata:
        if item["Name"] == "MpesaReceiptNumber":
            transaction_id = item["Value"]
        elif item["Name"] == "Amount":
            amount = item["Value"]
        elif item["Name"] == "PhoneNumber":
            phone = str(item["Value"])

    if result_code == 0:  # success
        payment = db.query(Payment).filter(Payment.phone_number == phone).order_by(Payment.created_at.desc()).first()
        if payment:
            payment.status = "success"
            payment.transaction_id = transaction_id
            booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
            if booking:
                booking.status = "paid"
            db.commit()
        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    else:
        return {"ResultCode": 1, "ResultDesc": "Failed"}

