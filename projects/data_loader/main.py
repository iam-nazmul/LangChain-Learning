"""
ChatAnthropic example with configuration options.

Install:
    pip install -U langchain-anthropic
"""


# pip install -U langchain-anthropic
# export ANTHROPIC_API_KEY="your-api-key"

from langchain_anthropic import ChatAnthropic

from dotenv import load_dotenv
load_dotenv()


model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    # temperature=,
    # max_tokens=,
    # timeout=,
    # max_retries=,
    # base_url="...",
    # Refer to API reference for full list of parameters
)

