# pip install -U langchain-anthropic
# export ANTHROPIC_API_KEY="your-api-key"

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

# model = ChatAnthropic(
#     model="claude-sonnet-4-5-20250929",
# )


model = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
)


# prompt = "Create a shider for Langchain Anthropic integration in Python. The shider should be a short poem that captures the essence of using Langchain with Anthropic's language models."

# prompt = "How to get job at anthropic?"
# prompt = "How to get job at anthropic? Typical roles available: ML/AI engineers give me a list of 10 roles with their description and skills required for each role."

# prompt = """
# ### 2. **ML Infrastructure Engineer**
# **Description:** Build scalable systems for training and serving large language models.
# **Skills Required:**
# - Distributed systems
# - Kubernetes, Docker
# - Python/C++
# - GPU/TPU optimization
# - MLOps & DevOps experience


# Create a strong resume for the above role. The resume should be tailored to highlight relevant experience, skills, and achievements that align with the requirements of an ML Infrastructure Engineer at Anthropic.
# """
prompt = """
### 5. **Software Engineer - API & Platform**
**Description:** Develop APIs and platforms for Claude's deployment and user interaction.
**Skills Required:**
- Backend development (Python/Go/Rust)
- API design & REST principles
- Database design (SQL/NoSQL)
- Scalability & performance optimization
- System design


Create a strong ATS format resume for the above role 
for me name: Md. Nazmul Hossain, 
email: nazmul.cse48@gmail.com,
github: https://github.com/iam-nazmul
linkedin: https://www.linkedin.com/in/iam-nazmul/
contact: +880 1761 777748,

The resume should be tailored to highlight relevant 
experience, skills, and achievements that align with 
the requirements of an Software Engineer - API & Platform 
at Anthropic.
"""


response = model.invoke(prompt)
print(response.content)

usage = response.usage_metadata
input_tokens = usage["input_tokens"]
output_tokens = usage["output_tokens"]

# Claude Haiku 4.5 pricing: $1.00 / 1M input tokens, $5.00 / 1M output tokens
input_cost = input_tokens * 1.00 / 1_000_000
output_cost = output_tokens * 5.00 / 1_000_000
total_cost = input_cost + output_cost

print(f"\nInput tokens: {input_tokens}")
print(f"Output tokens: {output_tokens}")
print(f"Total tokens: {usage['total_tokens']}")
print(f"Estimated cost: ${total_cost:.6f}")