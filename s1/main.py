# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন সহায়ক বাংলা শিক্ষক।"),
    ("human", "{topic} বিষয়টি একজন শিশুকে বোঝাও।"),
])
# model = ChatOpenAI(model="gpt-4o-mini")

# model = ChatOllama(model="gemma3:4b", temperature=0.3)
model = ChatOllama(model="gemma3:4b")
parser = StrOutputParser()

chain = prompt | model | parser          # ← এটাই LCEL
print(chain.invoke({"topic": "মাধ্যাকর্ষণ"}))


# ===============================================================

from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str = Field(description="সিনেমার নাম")
    rating: int = Field(description="১০-এর মধ্যে রেটিং")
    summary: str

structured_model = model.with_structured_output(MovieReview)
result = structured_model.invoke("Inception সিনেমাটির একটি রিভিউ দাও।")
print(result.title, result.rating, result.summary)
result = structured_model.invoke("Master সিনেমাটির একটি রিভিউ দাও।")
print(result.title, result.rating, result.summary)