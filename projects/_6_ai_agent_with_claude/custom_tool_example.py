"""
Claude Agent SDK example with a custom tool, using ClaudeSDKClient
for an interactive session.
"""

import asyncio
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ClaudeSDKClient,
)


@tool("greet", "Greet a user by name", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }


async def main():
    server = create_sdk_mcp_server(
        name="my-tools",
        version="1.0.0",
        tools=[greet_user],
    )

    options = ClaudeAgentOptions(
        mcp_servers={"my-tools": server},
        allowed_tools=["mcp__my-tools__greet"],
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Greet someone named Alex")
        async for message in client.receive_response():
            print(message)


if __name__ == "__main__":
    asyncio.run(main())
