
# app/utils/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_receipt_pdf(booking, payment):
    filename = f"receipt_{booking.id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Glow Haven Beauty Lounge - Receipt")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Customer: {booking.customer_name}")
    c.drawString(100, 750, f"Service: {booking.service_name}")
    c.drawString(100, 730, f"Date: {booking.date} {booking.time}")
    c.drawString(100, 710, f"Amount Paid: KES {payment.amount}")
    c.drawString(100, 690, f"Transaction ID: {payment.transaction_id}")
    c.drawString(100, 670, f"Status: {booking.status}")
    c.drawString(100, 650, f"Issue Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.save()
    return filename
