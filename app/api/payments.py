
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PaymentRequest(BaseModel):
    phone_number: str
    amount: float
    booking_id: str

@router.post("/deposit")
def pay_deposit(req: PaymentRequest):
    # Daraja integration will be implemented later
    return {
        "message": "Payment initiated (sandbox mode)",
        "phone_number": req.phone_number,
        "amount": req.amount
    }
