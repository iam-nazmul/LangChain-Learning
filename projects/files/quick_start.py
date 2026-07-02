"""
Minimal Claude Agent SDK example.

Install first:
    pip install claude-agent-sdk

Auth: the bundled Claude Code CLI will prompt you to log in
(subscription or API key) the first time you run this.
"""

import anyio
from claude_agent_sdk import query


async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)


if __name__ == "__main__":
    anyio.run(main)
