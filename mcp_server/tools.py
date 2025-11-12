
import httpx
from mcp.types import CallToolResult, TextContent
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
API_BASE_URL = "http://localhost:9000/api"


# -----------------------------------------------------
# 1️⃣ Services
# -----------------------------------------------------
@mcp.tool("get_services")
async def get_services() -> CallToolResult:
    """Fetch all available services."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/list")
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)


@mcp.tool("get_business_info")
async def get_business_info() -> CallToolResult:
    """Fetch general business information (e.g., hours, address)."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/")
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)


# -----------------------------------------------------
# 2️⃣ Booking + Payment Orchestration
# -----------------------------------------------------
@mcp.tool("complete_booking_flow")
async def complete_booking_flow(
    customer_name: str,
    phone_number: str,
    service_name: str,
    date: str,
    time: str
) -> CallToolResult:
    """
    Perform the full booking flow:
    - Verify service
    - Calculate 30% deposit
    - Initiate payment
    - Wait for confirmation
    - Generate receipt
    - Save booking
    - Add to Google Calendar
    """
    async with httpx.AsyncClient() as client:
        payload = {
            "customer_name": customer_name,
            "phone_number": phone_number,
            "service_name": service_name,
            "date": date,
            "time": time
        }
        res = await client.post(f"{API_BASE_URL}/bookings/full_flow", json=payload)

    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)


# -----------------------------------------------------
# 3️⃣ User Utilities
# -----------------------------------------------------
@mcp.tool("get_user_bookings")
async def get_user_bookings(phone_number: str) -> CallToolResult:
    """Fetch all bookings made by a given phone number."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/bookings/list")
        data = res.json() if res.headers.get("content-type", "").startswith("application/json") else None

        if isinstance(data, list):
            filtered = [b for b in data if b.get("phone_number") == phone_number]
            return CallToolResult(content=[TextContent(type="text", text=str(filtered))], isError=False)

    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)


@mcp.tool("submit_feedback")
async def submit_feedback(name: str, rating: int, comments: str) -> CallToolResult:
    """Submit user feedback."""
    async with httpx.AsyncClient() as client:
        payload = {"name": name, "rating": rating, "comments": comments}
        res = await client.post(f"{API_BASE_URL}/feedback/", json=payload)
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)


# -----------------------------------------------------
# Run MCP Server
# -----------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")

