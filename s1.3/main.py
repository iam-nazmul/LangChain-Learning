# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


from langchain_core.output_parsers import StrOutputParser

# model = ChatOpenAI(model="gpt-4o-mini")
model = ChatOllama(model="gemma3:4b", temperature=0.1)
parser = StrOutputParser()

chain = model | parser

result = chain.invoke("বাংলাদেশের রাজধানীর নাম কী?")
print(result)        # সরাসরি string
print(type(result))  # <class 'str'>


# ------------------------------------


from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("{topic} নিয়ে এক লাইনে বলো")
chain = prompt | model | parser

print(chain.invoke({"topic": "ক্রিকেট"}))


# ------------------------------------

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class MovieReview(BaseModel):
    title: str = Field(description="মুভির নাম")
    rating: int = Field(description="১ থেকে ১০ এর মধ্যে রেটিং")
    summary: str = Field(description="এক লাইনে রিভিউ সামারি")
    is_recommended: bool = Field(description="দেখা উচিত কিনা")

# model = ChatOpenAI(model="gpt-4o-mini")

model = ChatOllama(model="gemma3:4b", temperature=0.1)
structured_model = model.with_structured_output(MovieReview)

result = structured_model.invoke(
    "Interstellar মুভিটা নিয়ে একটা রিভিউ দাও"
)

print(result)
print(type(result))      # <class '__main__.MovieReview'>
print(result.title)      # সরাসরি অ্যাট্রিবিউট অ্যাক্সেস