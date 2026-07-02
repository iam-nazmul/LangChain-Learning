"""
Claude Agent SDK example with configuration options.

Install:
    pip install claude-agent-sdk
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",   # auto-accept file edits (use with care)
        cwd="agent_sdk_demo",  # working directory the agent operates in
        allowed_tools=["Read", "Write", "Edit", "Bash"],  # scope what it can touch
        max_turns=10,
    )

    async for message in query(
        prompt="Create a simple Python script that prints the first 10 Fibonacci numbers",
        options=options,
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
