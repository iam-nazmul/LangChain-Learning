
# 3. Output Parsers — মডেলের আউটপুটকে কাঠামোবদ্ধ করা (StrOutputParser, Pydantic দিয়ে structured output)।

আউটপুট পার্সারের ব্যাপারে বিস্তারিত আলোচনা করি — এটা LangChain এ একটা গুরুত্বপূর্ণ অংশ, কারণ মডেলের raw text output কে কাজে লাগানোর জন্য কাঠামোবদ্ধ ডেটায় রূপান্তর করা লাগে।

## কেন Output Parser লাগে

LLM মডেল সবসময় plain text রিটার্ন করে — `AIMessage` অবজেক্টের ভেতরে একটা স্ট্রিং থাকে। কিন্তু বাস্তব অ্যাপ্লিকেশনে আমাদের প্রায়ই দরকার হয়:
- শুধু স্ট্রিং, মেসেজ অবজেক্ট না
- নির্দিষ্ট ফিল্ডসহ JSON/dictionary
- Python অবজেক্ট (Pydantic model) যেটা validate করা যায়, type-safe

Output Parser এই গ্যাপটা পূরণ করে।

## ১. `StrOutputParser` — সবচেয়ে সহজ

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = model | parser

result = chain.invoke("বাংলাদেশের রাজধানীর নাম কী?")
print(result)        # সরাসরি string
print(type(result))  # <class 'str'>
```

`parser` ছাড়া হলে `model.invoke(...)` রিটার্ন করত একটা `AIMessage` অবজেক্ট, এবং টেক্সট পেতে `result.content` লিখতে হতো। `StrOutputParser` সেই `.content` extraction টা নিজেই করে দেয় — চেইনে বসিয়ে দিলে আউটপুট সরাসরি ক্লিন স্ট্রিং হয়ে যায়।

**LCEL চেইনে ব্যবহার:**

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("{topic} নিয়ে এক লাইনে বলো")
chain = prompt | model | parser

print(chain.invoke({"topic": "ক্রিকেট"}))
```

## ২. Pydantic দিয়ে Structured Output

এখানে দুইটা প্রধান উপায় আছে — পুরনো পদ্ধতি (`PydanticOutputParser`) আর আধুনিক পদ্ধতি (`with_structured_output`)। আধুনিক প্রজেক্টে দ্বিতীয়টাই বেশি ব্যবহৃত হয়।

### ক) আধুনিক পদ্ধতি: `with_structured_output()` (recommended)

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class MovieReview(BaseModel):
    title: str = Field(description="মুভির নাম")
    rating: int = Field(description="১ থেকে ১০ এর মধ্যে রেটিং")
    summary: str = Field(description="এক লাইনে রিভিউ সামারি")
    is_recommended: bool = Field(description="দেখা উচিত কিনা")

model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(MovieReview)

result = structured_model.invoke(
    "Interstellar মুভিটা নিয়ে একটা রিভিউ দাও"
)

print(result)
print(type(result))      # <class '__main__.MovieReview'>
print(result.title)      # সরাসরি অ্যাট্রিবিউট অ্যাক্সেস
print(result.rating)
```

এখানে `with_structured_output` মডেলের ফাংশন-কলিং (tool calling) ক্ষমতা ব্যবহার করে আউটপুটকে জোর করে সেই স্কিমার মধ্যে ফেলে দেয় — তাই এটা সবচেয়ে রিলায়েবল।

### খ) পুরনো পদ্ধতি: `PydanticOutputParser`

এটা কাজ করে prompt-এ format instruction যুক্ত করে — মডেলকে বলে দেওয়া হয় ঠিক কোন ফরম্যাটে JSON রিটার্ন করতে হবে।

```python
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
```

`parser.get_format_instructions()` যেই টেক্সটটা জেনারেট করে, সেটা মডেলকে বলে দেয় ঠিক কোন JSON schema মেনে আউটপুট দিতে হবে। এই পদ্ধতিতে মডেল কখনো কখনো ভুল ফরম্যাটে আউটপুট দিতে পারে (বিশেষ করে ছোট/দুর্বল মডেলে), তাই parsing error হ্যান্ডেল করার জন্য `OutputFixingParser` বা `RetryOutputParser` ব্যবহার করা যায়।

## কোনটা কখন ব্যবহার করবেন

| পরিস্থিতি | পার্সার |
|---|---|
| সাধারণ টেক্সট চাই | `StrOutputParser` |
| নির্দিষ্ট ফিল্ড দরকার, রিলায়েবল মডেল (OpenAI/Anthropic) | `with_structured_output()` |
| ফাংশন-কলিং সাপোর্ট নেই এমন মডেল | `PydanticOutputParser` + format instructions |
| nested structure / list of objects | `with_structured_output()`, Pydantic-এ `List[SubModel]` দিয়ে |

## একটা প্র্যাক্টিকাল উদাহরণ — একসাথে দেখি

```python
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

model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(Recipe)

prompt = ChatPromptTemplate.from_template("{dish} রান্নার রেসিপি দাও")
chain = prompt | structured_model

result = chain.invoke({"dish": "খিচুড়ি"})

print(result.dish_name)
for ing in result.ingredients:
    print(f"- {ing.name}: {ing.quantity}")
```

এখানে `List[Ingredient]` এর মত nested Pydantic model ব্যবহার করেও কোনো সমস্যা হয় না — `with_structured_output` জটিল nested স্কিমাও ঠিকঠাক হ্যান্ডেল করে।

---

আপনি কি এখন এই টপিকটা নিয়ে একটা ছোট হ্যান্ডস-অন এক্সারসাইজ চান (যেমন একটা real-world ডেটা এক্সট্রাকশন টাস্ক), নাকি পরের টপিকে (যেমন `JsonOutputParser` বা Output Parser এর error handling) যাওয়া যাক?