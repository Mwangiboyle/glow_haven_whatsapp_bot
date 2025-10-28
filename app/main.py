
from fastapi import FastAPI
from app.api import services, bookings, payments, receipts, feedback

app = FastAPI(title="Glow Haven Beauty Lounge API")

# Routers
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(receipts.router, prefix="/api/receipts", tags=["Receipts"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])

@app.get("/")
def root():
    return {"message": "Glow Haven Beauty Lounge API is running"}
