# app/api/receipts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Booking, Payment
from fpdf import FPDF
import os
from datetime import datetime

router = APIRouter(prefix="/api/receipts", tags=["Receipts"])

def generate_receipt_pdf(booking: Booking, payment: Payment) -> str:
    """Generate a PDF receipt using FPDF library"""
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RECEIPT", ln=True, align="C")
    pdf.ln(10)

    # Receipt details
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Receipt Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 10, f"Booking ID: {booking.id}", ln=True)
    pdf.cell(0, 10, f"Payment ID: {payment.id}", ln=True)
    pdf.ln(5)

    # Booking information
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Booking Details", ln=True)
    pdf.set_font("Arial", "", 12)

    # Add booking details (adjust based on your Booking model attributes)
    if hasattr(booking, 'customer_name'):
        pdf.cell(0, 10, f"Customer: {booking.customer_name}", ln=True)
    if hasattr(booking, 'service'):
        pdf.cell(0, 10, f"Service: {booking.service}", ln=True)
    if hasattr(booking, 'booking_date'):
        pdf.cell(0, 10, f"Date: {booking.booking_date}", ln=True)

    pdf.ln(5)

    # Payment information
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Payment Details", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Amount: ${payment.amount:.2f}", ln=True)
    pdf.cell(0, 10, f"Payment Method: {payment.payment_method if hasattr(payment, 'payment_method') else 'N/A'}", ln=True)
    pdf.cell(0, 10, f"Status: {payment.status}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank you for your business!", ln=True, align="C")

    # Save PDF
    os.makedirs("receipts", exist_ok=True)
    filename = f"receipts/receipt_{booking.id}_{payment.id}.pdf"
    pdf.output(filename)

    return filename

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
