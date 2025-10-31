
# app/api/bookings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import Booking
from app.models import BookingCreate, BookingResponse

# Google Calendar imports
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

# Google Calendar helpers
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
GOOGLE_CALENDAR_TIMEZONE = os.getenv("GOOGLE_CALENDAR_TIMEZONE", "Africa/Nairobi")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def _get_calendar_service():
    if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
        raise RuntimeError("Google credentials not configured. Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON path.")
    if not GOOGLE_CALENDAR_ID:
        raise RuntimeError("Google Calendar ID not set. Set GOOGLE_CALENDAR_ID.")
    creds = Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)

def _booking_to_event_payload(booking: Booking) -> dict:
    # Combine booking date and time into start datetime; assume 1-hour duration
    start_dt = datetime.combine(booking.date, booking.time)
    end_dt = start_dt + timedelta(hours=1)
    description = f"Service: {booking.service_name}\nCustomer: {booking.customer_name}\nPhone: {booking.phone_number}\nAmount: KES {booking.amount}\nStatus: {booking.status}"
    return {
        "summary": f"Glow Haven: {booking.service_name} ({booking.customer_name})",
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": GOOGLE_CALENDAR_TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": GOOGLE_CALENDAR_TIMEZONE},
    }

def create_calendar_event_for_booking(booking: Booking) -> str:
    """Create a Google Calendar event for the given booking, return eventId."""
    service = _get_calendar_service()
    event_body = _booking_to_event_payload(booking)
    event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event_body).execute()
    return event.get("id")

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

    # Create Google Calendar event if not already linked
    try:
        if not new_booking.id:
            event_id = create_calendar_event_for_booking(new_booking)
            new_booking.id = event_id
            db.commit()
            db.refresh(new_booking)
    except Exception:
        # Fail open: booking creation should not fail due to calendar issues
        pass

    return new_booking


@router.get("/list", response_model=list[BookingResponse])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

@router.post("/sync_calendar")
def sync_calendar(db: Session = Depends(get_db)):
    """Create calendar events for bookings missing calendar_event_id."""
    missing = db.query(Booking).filter(Booking.id.is_(None)).all()
    created = 0
    errors = 0
    for b in missing:
        try:
            event_id = create_calendar_event_for_booking(b)
            b.calendar_event_id = event_id
            created += 1
        except Exception:
            errors += 1
    db.commit()
    return {"created": created, "errors": errors}


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

