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



# ------------------------------------

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

class Person(BaseModel):
    name: str = Field(description="মানুষের নাম")
    age: int = Field(description="বয়স")
    city: str = Field(description="শহরের নাম")

parser = PydanticOutputParser(pydantic_object=Person)

prompt = ChatPromptTemplate.from_template(
    "নিচের তথ্য থেকে ডেটা এক্সট্রাক্ট করো।\n"
    "{format_instructions}\n"
    "তথ্য: {input}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser

result = chain.invoke({
    "input": "করিমের বয়স ২৮ বছর, সে ঢাকায় থাকে।"
})

print(result)         # Person(name='করিম', age=28, city='ঢাকা')
print(result.age + 2) # 30 — সরাসরি গণনা করা যায়


# ------------------------------------

from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class Ingredient(BaseModel):
    name: str
    quantity: str

class Recipe(BaseModel):
    dish_name: str = Field(description="খাবারের নাম")
    ingredients: List[Ingredient] = Field(description="উপকরণের লিস্ট")
    steps: List[str] = Field(description="রান্নার ধাপগুলো")

# model = ChatOpenAI(model="gpt-4o-mini")
model = ChatOllama(model="gemma3:4b", temperature=0.1)
structured_model = model.with_structured_output(Recipe)

prompt = ChatPromptTemplate.from_template("{dish} রান্নার রেসিপি দাও")
chain = prompt | structured_model

# result = chain.invoke({"dish": "খিচুড়ি"})

result = chain.invoke({"dish": "Basmoti Kachchi"})

print(result.dish_name)
for ing in result.ingredients:
    print(f"- {ing.name}: {ing.quantity}")
print("\nরান্নার ধাপগুলো:")
for step in result.steps:
    print(f"- {step}")

