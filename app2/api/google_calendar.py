
import datetime
import asyncio
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your JSON key file
SERVICE_ACCOUNT_FILE = "google_cred.json"

# The ID of your shared Google Calendar
CALENDAR_ID = "mwangiboyle4@gmail.com"

# Define scope
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Authenticate with service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Optional: Impersonate the calendar owner (if needed)
# credentials = credentials.with_subject("your_business_email@gmail.com")

service = build("calendar", "v3", credentials=credentials)


async def add_to_calendar(customer_name: str, date: str, time: str, service_name: str):
    """
    Adds a booking to the shared business calendar using a service account.
    Returns a public Google Calendar link.
    """
    booking_date = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_time = booking_date + datetime.timedelta(hours=1)

    event = {
        "summary": f"{service_name} - {customer_name}",
        "location": "Glow Haven Beauty Lounge",
        "description": f"{customer_name}'s {service_name} appointment at Glow Haven.",
        "start": {
            "dateTime": booking_date.isoformat(),
            "timeZone": "Africa/Nairobi",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Africa/Nairobi",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 30},
                {"method": "email", "minutes": 60},
            ],
        },
    }

    event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return event_result.get("htmlLink")


# 🧪 Test
if __name__ == "__main__":
    async def test_calendar():
        link = await add_to_calendar(
            customer_name="Jane Doe",
            date="2025-11-13",
            time="15:00",
            service_name="Pedicure"
        )
        print("✅ Event created successfully!")
        print("🔗 Event link:", link)

    asyncio.run(test_calendar())
