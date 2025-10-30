
# app/api/receipts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Booking, Payment
from app.utils.pdf_generator import generate_receipt_pdf
import os

router = APIRouter(prefix="/api/receipts", tags=["Receipts"])

@router.post("/generate/{booking_id}")
def generate_receipt(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    payment = db.query(Payment).filter(Payment.booking_id == booking.id, Payment.status == "success").first()
    if not payment:
        raise HTTPException(status_code=400, detail="Payment not completed")

    filename = generate_receipt_pdf(booking, payment)
    file_path = os.path.abspath(filename)
    return {"receipt_path": file_path}

