# 2. Prompt Templates — ডায়নামিক ইনপুট সহ প্রম্পট তৈরি (ChatPromptTemplate)। 
Prompt Templates নিয়ে বিস্তারিত বাংলায় ব্যাখ্যা দিচ্ছি।

## কেন Prompt Template লাগে?

প্রতিবার হার্ডকোড করা স্ট্রিং দিয়ে মেসেজ বানানো অপ্রয়োজনীয় ও ভুলপ্রবণ। ধরুন আপনি একটা অনুবাদ অ্যাপ বানাচ্ছেন — ইউজার ভাষা ও টেক্সট দিলে সেটা প্রম্পটে বসাতে হবে। এই **ডায়নামিক ভ্যালু ইনজেক্ট** করার কাজটাই করে `PromptTemplate` / `ChatPromptTemplate`।

## ১. বেসিক `ChatPromptTemplate`

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন {language} ভাষা বিশেষজ্ঞ অনুবাদক।"),
    ("human", "এই বাক্যটা {target_language}-এ অনুবাদ করো: {text}")
])

prompt = template.invoke({
    "language": "বাংলা",
    "target_language": "ইংরেজি",
    "text": "আমি ভাত খাচ্ছি।"
})

print(prompt.to_messages())
```

আউটপুট হবে `SystemMessage` ও `HumanMessage`-এর একটা লিস্ট — `{}` এর জায়গায় আসল ভ্যালু বসে গেছে।

`{variable_name}` সিনট্যাক্স দিয়ে যেকোনো জায়গায় placeholder রাখা যায় — system, human, কোনো role-এই কাজ করে।

## ২. Model-এর সাথে Chain করা

```python
model = ChatOpenAI(model="gpt-4o")

chain = template | model  # LCEL pipe operator দিয়ে chain বানানো

response = chain.invoke({
    "language": "বাংলা",
    "target_language": "ফরাসি",
    "text": "শুভ সকাল"
})

print(response.content)
```

`template | model` — এটাই LangChain-এর **LCEL (LangChain Expression Language)**। Template প্রথমে রান হয়ে messages বানায়, তারপর সেটা model-এ যায়।

## ৩. `MessagesPlaceholder` — Conversation History ইনজেক্ট করা

যদি আগের কথোপকথন (history) ডায়নামিকভাবে বসাতে হয়:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

template = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন সহায়ক বাংলা সহকারী।"),
    MessagesPlaceholder(variable_name="history"),   # এখানে আগের সব মেসেজ বসবে
    ("human", "{question}")
])

chat_history = [
    HumanMessage(content="আমার নাম রাহুল।"),
    AIMessage(content="ঠিক আছে রাহুল, কী সাহায্য করতে পারি?"),
]

prompt = template.invoke({
    "history": chat_history,
    "question": "আমার নাম কী বলেছিলাম?"
})
```

এটা multi-turn chatbot বানানোর সময় খুব দরকারি — পুরো history-কে একটা ভ্যারিয়েবল হিসেবে ইনজেক্ট করা যায়।

## ৪. Few-Shot Prompting (উদাহরণসহ প্রম্পট)

মডেলকে কয়েকটা উদাহরণ দেখিয়ে শেখাতে চাইলে:

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate

examples = [
    {"input": "ভালো", "output": "Good"},
    {"input": "খারাপ", "output": "Bad"},
]

example_template = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_template,
    examples=examples,
)

final_template = ChatPromptTemplate.from_messages([
    ("system", "তুমি বাংলা থেকে ইংরেজি অনুবাদ করো। নিচের প্যাটার্ন অনুসরণ করো।"),
    few_shot_prompt,
    ("human", "{input}")
])

prompt = final_template.invoke({"input": "সুন্দর"})
```

## ৫. Partial Variables — কিছু ভ্যালু আগেই ফিক্স করা

যদি একটা ভ্যারিয়েবল সবসময় একই থাকে (যেমন তারিখ, ভাষা):

```python
from datetime import date

template = ChatPromptTemplate.from_messages([
    ("system", "আজকের তারিখ {current_date}। তুমি একজন সহায়ক সহকারী।"),
    ("human", "{question}")
])

template = template.partial(current_date=str(date.today()))

# এখন শুধু question দিলেই চলবে
prompt = template.invoke({"question": "আজ কী দিন?"})
```

## ৬. `from_template` দিয়ে সরাসরি স্ট্রিং থেকে

```python
from langchain_core.prompts import HumanMessagePromptTemplate

human_template = HumanMessagePromptTemplate.from_template(
    "নিচের প্রশ্নের উত্তর {style} স্টাইলে দাও:\n{question}"
)
```

## গুরুত্বপূর্ণ পয়েন্ট — `invoke()` vs `format()`

| পদ্ধতি | রিটার্ন করে |
|---|---|
| `template.invoke({...})` | `ChatPromptValue` অবজেক্ট (LCEL-friendly, recommended) |
| `template.format_messages({...})` | সরাসরি messages-এর লিস্ট |
| `template.format({...})` | একটা স্ট্রিং (সাধারণত non-chat কাজে) |

LangChain-এর বর্তমান ভার্সনে `invoke()` ব্যবহার করাই standard practice, কারণ এটা LCEL chain-এর সাথে সরাসরি কাজ করে।

## একটা পূর্ণ বাস্তব উদাহরণ — কাস্টমার সাপোর্ট বট

```python
template = ChatPromptTemplate.from_messages([
    ("system", """তুমি {company_name}-এর কাস্টমার সাপোর্ট এজেন্ট।
নিয়মাবলী:
- {tone} টোনে কথা বলবে
- উত্তর {max_words} শব্দের মধ্যে রাখবে"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{user_input}")
])

chain = template | model

response = chain.invoke({
    "company_name": "TechBangla",
    "tone": "বিনয়ী ও পেশাদার",
    "max_words": "৫০",
    "history": [],
    "user_input": "আমার অর্ডার কোথায় জানতে চাই।"
})
```

---

পরের ধাপে কোনটা দেখতে চান — **Output Parsers** (মডেলের আউটপুটকে structured JSON/Pydantic অবজেক্টে রূপান্তর), নাকি **LCEL chains** নিয়ে আরও গভীরে (যেমন `RunnableSequence`, `RunnableParallel`)?