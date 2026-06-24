"""
Prompt Templates — ডায়নামিক ইনপুট সহ প্রম্পট তৈরি
======================================================
ChatPromptTemplate দিয়ে আমরা প্রম্পটকে একটি "ছাঁচ" (template) হিসেবে বানাই।
প্রতিবার invoke করার সময় ভ্যারিয়েবল বদলে দিলেই নতুন প্রম্পট তৈরি হয়।
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOllama(model="gemma3:4b", temperature=0.5)
parser = StrOutputParser()

print("=" * 60)
print("১. from_template() — সবচেয়ে সহজ পদ্ধতি")
print("=" * 60)

# PromptTemplate শুধু একটি মেসেজের জন্য (human)
simple_prompt = PromptTemplate.from_template(
    "{language} প্রোগ্রামিং ভাষা সম্পর্কে ৩টি মজার তথ্য বলো।"
)

# .format() দিয়ে দেখা যায় প্রম্পট কেমন হবে
print("Formatted prompt:")
print(simple_prompt.format(language="Python"))
print()

chain = simple_prompt | model | parser
print("আউটপুট:", chain.invoke({"language": "Python"}))
print()


print("=" * 60)
print("২. from_messages() — System + Human মেসেজ আলাদা")
print("=" * 60)

# সবচেয়ে বেশি ব্যবহৃত পদ্ধতি
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন {role}। তুমি সবসময় {style} ভাষায় উত্তর দাও।"),
    ("human", "{question}"),
])

# কোন ভ্যারিয়েবলগুলো দরকার দেখো
print("Input variables:", chat_prompt.input_variables)
print()

# প্রম্পট কেমন দেখতে হবে তা inspect করো
messages = chat_prompt.format_messages(
    role="Python বিশেষজ্ঞ",
    style="সহজ বাংলা",
    question="List কী?"
)
for msg in messages:
    print(f"[{msg.type}]: {msg.content}")
print()

chain = chat_prompt | model | parser
result = chain.invoke({
    "role": "ইতিহাস শিক্ষক",
    "style": "গল্পের",
    "question": "মুঘল সাম্রাজ্যের পতনের কারণ কী?"
})
print("আউটপুট:", result)
print()


print("=" * 60)
print("৩. একাধিক ইনপুট — বহু ভ্যারিয়েবল")
print("=" * 60)

# কোড রিভিউ করার টেমপ্লেট
code_review_prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন সিনিয়র {language} ডেভেলপার। কোড রিভিউ করো।"),
    ("human", """
নিচের কোডটি রিভিউ করো:

```{language}
{code}
```

বিশেষভাবে দেখো: {focus_area}
"""),
])

chain = code_review_prompt | model | parser
result = chain.invoke({
    "language": "Python",
    "code": "def add(a,b):\n    return a+b",
    "focus_area": "naming convention এবং type hints"
})
print("কোড রিভিউ:", result)
print()


print("=" * 60)
print("৪. from_template() দিয়ে partial variables")
print("=" * 60)

# partial() — কিছু ভ্যারিয়েবল আগেই fix করে রাখা
base_prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি {company} কোম্পানির {role}।"),
    ("human", "{user_message}"),
])

# company আগেই fix করা
company_prompt = base_prompt.partial(company="TechBD")

chain = company_prompt | model | parser
result = chain.invoke({
    "role": "কাস্টমার সার্ভিস এজেন্ট",
    "user_message": "আমার অর্ডার কোথায়?"
})
print("Partial template আউটপুট:", result)
print()


print("=" * 60)
print("৫. Conversation History সহ Template")
print("=" * 60)

from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# MessagesPlaceholder দিয়ে পুরো কথোপকথন ইঞ্জেক্ট করা যায়
conversation_prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন সহায়ক AI।"),
    MessagesPlaceholder(variable_name="history"),  # ← পুরানো কথোপকথন
    ("human", "{current_message}"),
])

# আগের কথোপকথনের ইতিহাস
history = [
    HumanMessage(content="আমার নাম নাজমুল।"),
    AIMessage(content="ঠিক আছে নাজমুল, আমি মনে রাখব।"),
]

chain = conversation_prompt | model | parser
result = chain.invoke({
    "history": history,
    "current_message": "আমার নাম কী বলতে পারবে?"
})
print("Conversation সহ আউটপুট:", result)
print()


print("=" * 60)
print("৬. invoke() vs batch() — একসাথে অনেক ইনপুট")
print("=" * 60)

topic_prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন বিজ্ঞান শিক্ষক।"),
    ("human", "{topic} এক লাইনে ব্যাখ্যা করো।"),
])

chain = topic_prompt | model | parser

# batch() — একবারে অনেক প্রশ্ন পাঠাও
topics = [
    {"topic": "আলোর গতি"},
    {"topic": "মাধ্যাকর্ষণ"},
    {"topic": "পরমাণু"},
]

results = chain.batch(topics)
for topic, result in zip(topics, results):
    print(f"• {topic['topic']}: {result}")
