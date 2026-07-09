# pip install -U langchain-anthropic
# export ANTHROPIC_API_KEY="your-api-key"

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

model = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
)

prompt = "Create Cantain Shift Report for Ritmise"

print(model.invoke(prompt).content)