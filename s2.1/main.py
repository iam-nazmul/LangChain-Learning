from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

# model="qwen/qwen3-32b",
model = "openai/gpt-oss-120b"

llm = ChatGroq(
    model=model,
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
)



messages = [
    (
        "system",
        "You are a senior and lead software engineer with 10 years of experience. You are an expert in programming and software development. You are a helpful assistant.",
    ),
    ("human", "Give me a langchain guideline for best practices for professionals in bangla."),
]

ai_msg = llm.invoke(messages)

print(ai_msg.content)