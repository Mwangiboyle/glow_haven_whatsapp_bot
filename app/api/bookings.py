
# app/api/bookings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Booking
from app.models import BookingCreate, BookingResponse

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

@router.post("/create", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    new_booking = Booking(
        customer_name=booking.customer_name,
        phone_number=booking.phone_number,
        service_name=booking.service_name,
        date=booking.date,
        time=booking.time,
        amount=booking.amount,
        status="pending"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("/list", response_model=list[BookingResponse])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

