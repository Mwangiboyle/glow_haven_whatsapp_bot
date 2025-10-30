import os
import json
import asyncio
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv
from .memory import init_memory_db, load_memory, save_memory

# initialize once
init_memory_db()

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# In-memory per-user chat memory (simple, process-local)
CONVERSATIONS = {}
CONV_LOCK = asyncio.Lock()

# Shared MCP server parameters
MCP_SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=["mcp_server/tools.py"],
    env=None,
)

# Cached tools and lock for concurrency-safe one-time init
TOOLS_CACHE = None
TOOLS_LOCK = asyncio.Lock()

async def load_tools_once():
    global TOOLS_CACHE
    if TOOLS_CACHE is not None:
        return TOOLS_CACHE
    async with TOOLS_LOCK:
        if TOOLS_CACHE is not None:
            return TOOLS_CACHE
        # Open a short-lived session just to list tools once
        async with stdio_client(MCP_SERVER_PARAMS) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in tools_result.tools
        ]
        TOOLS_CACHE = tools
        return tools

async def chat_with_bot(user_message: str, user_id: str | None = None) -> str:
    """
    Send a message to OpenAI with MCP tools available.
    If user_id is provided, maintain short-term chat memory per user.
    """

    # Ensure tools are loaded once and cached
    tools = await load_tools_once()

    # Build conversation with optional memory
    async with CONV_LOCK:
        history = load_memory(user_id) if user_id else []
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for Glow Haven Beauty Lounge."
                    "All the prices are in kenya shillings."
                    "Help customers with bookings, questions about services, and general inquiries. "
                    "Be friendly and professional. Do not answer questions outside the business. "
                    "Customers can book services and pay a 30% deposit via M-Pesa. "
                    "Always calculate the deposit as 30% of the total service price before initiating payment."
                )
            }
        ] + history + [{"role": "user", "content": user_message}]

    # Current user turn
    messages.append({"role": "user", "content": user_message})

    # First call to OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # If tools are requested, call them via a short-lived MCP session
    if assistant_message.tool_calls:
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ],
        })

        async with stdio_client(MCP_SERVER_PARAMS) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    result = await session.call_tool(tool_name, arguments=tool_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text,
                    })

        # Second call to OpenAI with tool results
        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        final_text = final_response.choices[0].message.content
    else:
        # Direct response without tools
        final_text = assistant_message.content

    # Update memory with the latest user/assistant turns (cap size)

    if user_id:
        convo = history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": final_text},
        ]
        save_memory(user_id, convo)



    return final_text

async def main():
    print("=" * 60)
    print("🌟 Glow Haven Beauty Lounge - Chat Bot")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Have a beautiful day!")
            break

        if not user_input:
            continue

        try:
            response = await chat_with_bot(user_input)
            print(f"🤖 Bot: {response}\n")
            print("-" * 60)

        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    asyncio.run(main())
