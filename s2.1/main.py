from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)

messages = [
    (
        "system",
        "You are lead software engineer. You are an expert in programming and software development. You are a helpful assistant.",
    ),
    ("human", "Give me a langchain guideline for best practices."),
]

ai_msg = llm.invoke(messages)

print(ai_msg.content)