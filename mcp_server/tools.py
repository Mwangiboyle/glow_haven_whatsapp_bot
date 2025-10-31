
import httpx
from mcp.types import CallToolResult, TextContent
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
API_BASE_URL = "http://localhost:9000/api"


@mcp.tool("get_services")
async def get_services() -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/list")
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("get_business_info")
async def get_business_info() -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/")
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("get_user_bookings")
async def get_user_bookings(phone_number: str, customer_name: str = "") -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/bookings/list")
        data = res.json() if res.headers.get("content-type", "").startswith("application/json") else None
        if isinstance(data, list):
            filtered = [b for b in data if b.get("phone_number") == phone_number]
            if customer_name:
                filtered = [b for b in filtered if b.get("customer_name", "").strip().lower() == customer_name.strip().lower()]
            return CallToolResult(content=[TextContent(type="text", text=str(filtered))], isError=False)
        return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("create_booking")
async def create_booking(customer_name: str, phone_number: str, service_name: str, date: str, time: str, amount: float) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {
            "customer_name": customer_name,
            "phone_number": phone_number,
            "service_name": service_name,
            "date": date,
            "time": time,
            "amount": amount,
        }
        res = await client.post(f"{API_BASE_URL}/bookings/create", json=payload)
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("initiate_payment")
async def initiate_payment(phone_number: str, amount: float, booking_id: int) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {"phone_number": phone_number, "amount": amount, "booking_id": booking_id}
        res = await client.post(f"{API_BASE_URL}/payments/stkpush", json=payload)
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("submit_feedback")
async def submit_feedback(name: str, rating: int, comments: str) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {"name": name, "rating": rating, "comments": comments}
        res = await client.post(f"{API_BASE_URL}/feedback/", json=payload)
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("generate_receipt")
async def generate_receipt(booking_id: int) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{API_BASE_URL}/receipts/generate/{booking_id}")
    return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("find_booking")
async def find_booking(customer_name: str, service_name: str = "") -> CallToolResult:
    """Return latest booking(s) for a customer (optionally filter by service)."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/bookings/list")
        data = res.json() if res.headers.get("content-type", "").startswith("application/json") else None
        if isinstance(data, list):
            filtered = [b for b in data if b.get("customer_name", "").strip().lower() == customer_name.strip().lower()]
            if service_name:
                filtered = [b for b in filtered if b.get("service_name", "").strip().lower() == service_name.strip().lower()]
            filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return CallToolResult(content=[TextContent(type="text", text=str(filtered))], isError=False)
        return CallToolResult(content=[TextContent(type="text", text=res.text)], isError=False)

@mcp.tool("poll_payment_status")
async def poll_payment_status(booking_id: int, timeout_seconds: int = 30, interval_seconds: int = 3) -> CallToolResult:
    import asyncio as _asyncio
    async with httpx.AsyncClient() as client:
        remaining = timeout_seconds
        while remaining > 0:
            res = await client.get(f"{API_BASE_URL}/payments/status/{booking_id}")
            text = res.text
            if any(s in text for s in ["success", "failed", "not_found"]):
                return CallToolResult(content=[TextContent(type="text", text=text)], isError=False)
            await _asyncio.sleep(interval_seconds)
            remaining -= interval_seconds
    return CallToolResult(content=[TextContent(type="text", text="timeout")], isError=False)

if __name__ == "__main__":
    # Start an HTTP server on port 8000
    mcp.run(transport="stdio")
