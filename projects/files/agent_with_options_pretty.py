"""
Claude Agent SDK example with configuration options.

Install:
    pip install claude-agent-sdk
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
)


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer with 6+ years of experience",
        permission_mode="acceptEdits",   # auto-accept file edits (use with care)
        cwd="/",            # working directory the agent operates in
        allowed_tools=["Read", "Write", "Edit", "Bash"],  # scope what it can touch
        max_turns=10,
    )

    async for message in query(
        prompt="Create a resume for a Python developer with 6+ years of experience, highlighting skills in web development, data analysis, and machine learning. Include a brief summary, work experience, education, and relevant projects.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n🤖 {block.text}")
                elif isinstance(block, ThinkingBlock):
                    print(f"\n💭 (thinking) {block.thinking[:200]}...")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n🔧 Using {block.name}({_format_input(block.input)})")
                elif isinstance(block, ToolResultBlock):
                    status = "❌" if block.is_error else "✅"
                    print(f"{status} {_format_tool_result(block.content)}")

        elif isinstance(message, ResultMessage):
            print("\n" + "─" * 50)
            print(f"✅ Done in {message.num_turns} turn(s), "
                  f"{message.duration_ms / 1000:.1f}s")
            if message.total_cost_usd is not None:
                print(f"💵 Cost: ${message.total_cost_usd:.4f}")
            if message.is_error:
                print(f"⚠️  Finished with an error (subtype: {message.subtype})")


def _format_input(input_dict: dict) -> str:
    """Compact one-line preview of a tool's input args."""
    if not input_dict:
        return ""
    parts = []
    for k, v in input_dict.items():
        s = str(v)
        if len(s) > 60:
            s = s[:60] + "…"
        parts.append(f"{k}={s!r}")
    return ", ".join(parts)


def _format_tool_result(content) -> str:
    """Compact one-line preview of a tool's result content."""
    if content is None:
        return "(no output)"
    if isinstance(content, str):
        text = content
    else:
        # list[dict[str, Any]] — pull text fields out
        text = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    text = text.strip().replace("\n", " ")
    return text[:120] + ("…" if len(text) > 120 else "")


if __name__ == "__main__":
    asyncio.run(main())
