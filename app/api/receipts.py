
from fastapi import APIRouter

router = APIRouter()

@router.get("/{booking_id}")
def generate_receipt(booking_id: str):
    # PDF generation to be added later
    return {"message": f"Receipt for booking {booking_id} will be generated"}
