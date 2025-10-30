import os
import json
import asyncio
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def chat_with_bot(user_message: str) -> str:
    """
    Send a message to OpenAI with MCP tools available
    """
    print(f"\n💬 You: {user_message}")
    print("🤔 Thinking...\n")

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/tools.py"],
        env=None
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize MCP
            await session.initialize()

            # Get available tools
            tools_result = await session.list_tools()

            # Convert MCP tools to OpenAI format
            tools = []
            for tool in tools_result.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            print(f"🔧 Loaded {len(tools)} tools: {[t['function']['name'] for t in tools]}\n")

            # First call to OpenAI
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant for Glow Haven Beauty
                        Lounge. Help customers with bookings, questions about services,
            and general inquiries. Be friendly and professional. Do not answer questions
            outside the business."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]

            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4-turbo-preview"
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Check if OpenAI wants to use tools
            if assistant_message.tool_calls:
                print(f"🔧 OpenAI wants to call {len(assistant_message.tool_calls)} tool(s):\n")

                # Add assistant message to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call via MCP
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"  → Calling: {tool_name}")
                    print(f"    Args: {tool_args}")

                    # Call the tool via MCP
                    result = await session.call_tool(tool_name, arguments=tool_args)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result.content[0].text
                    })

                    print(f"    ✅ Result: {result.content[0].text[:100]}...\n")

                # Second call to OpenAI with tool results
                print("🤔 Getting final response...\n")
                final_response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools
                )

                return final_response.choices[0].message.content

            else:
                # Direct response without tools
                return assistant_message.content

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
