
# app/schemas.py
from sqlalchemy import Column, Integer, String, Float, Date, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(String, default="pending")  # pending, paid, cancelled
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payment = relationship("Payment", back_populates="booking", uselist=False)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    phone_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String, unique=True, nullable=True)
    status = Column(String, default="initiated")  # initiated, success, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")
