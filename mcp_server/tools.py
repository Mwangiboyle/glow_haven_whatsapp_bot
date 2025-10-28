
import httpx
from mcp.types import CallToolResult, TextContent
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()
API_BASE_URL = "http://localhost:8000/api"


@mcp.tool("get_services")
async def get_services() -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/list/")
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("get_business_info")
async def get_business_info() -> CallToolResult:
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{API_BASE_URL}/services/")
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("create_booking")
async def create_booking(name: str, phone: str, service: str, date: str, time: str) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {"name": name, "phone": phone, "service": service, "date": date, "time": time}
        res = await client.post(f"{API_BASE_URL}/bookings/", json=payload)
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("initiate_payment")
async def initiate_payment(phone_number: str, amount: float, booking_id: str) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {"phone_number": phone_number, "amount": amount, "booking_id": booking_id}
        res = await client.post(f"{API_BASE_URL}/payments/deposit/", json=payload)
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)

@mcp.tool("submit_feedback")
async def submit_feedback(name: str, rating: int, comments: str) -> CallToolResult:
    async with httpx.AsyncClient() as client:
        payload = {"name": name, "rating": rating, "comments": comments}
        res = await client.post(f"{API_BASE_URL}/feedback/", json=payload)
    return CallToolResult(content=[TextContent(type="text",text=res.text)],isError=False)



