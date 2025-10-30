
# app/models.py
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional

# ----------- BOOKINGS -----------
class BookingCreate(BaseModel):
    customer_name: str
    phone_number: str
    service_name: str
    date: date
    time: time
    amount: float

class BookingResponse(BaseModel):
    id: int
    customer_name: str
    phone_number: str
    service_name: str
    date: date
    time: time
    status: str
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


# ----------- PAYMENTS -----------
class PaymentCreate(BaseModel):
    booking_id: int
    phone_number: str
    amount: float

class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    phone_number: str
    amount: float
    transaction_id: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
