
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BookingRequest(BaseModel):
    name: str
    phone: str
    service: str
    date: str
    time: str

@router.post("/")
def create_booking(req: BookingRequest):
    # Google Calendar integration will come later
    return {
        "message": "Booking request received",
        "details": req.model_dump()
    }

@router.get("/")
def get_bookings():
    return {"message": "List of bookings (placeholder)"}
