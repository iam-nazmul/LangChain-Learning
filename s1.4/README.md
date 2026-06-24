
# 4. __*LCEL*__ ও __*Runnables*__ — `invoke`, `batch`, `stream`; এবং `RunnableParallel`, `RunnablePassthrough`, `RunnableBranch`


# LCEL এবং Runnables

LCEL (LangChain Expression Language) হলো LangChain-এর একটা declarative syntax, যেখানে `|` (pipe) operator দিয়ে বিভিন্ন component একসাথে chain করা যায়। প্রতিটা component — prompt, model, parser, retriever — সবগুলোই **Runnable** interface implement করে, তাই তাদের আচরণ একইরকম predictable হয়।

```python
chain = prompt | model | output_parser
```

এই pipe-এর মাধ্যমে একটার output পরের ধাপের input হিসেবে চলে যায়। যেহেতু সবকিছুই Runnable, তাই সব Runnable-এর কিছু common method আছে — `invoke`, `batch`, `stream` (এবং async ভার্সন `ainvoke`, `abatch`, `astream`)।

---

## invoke — একটা input, একটা output

`invoke()` সবচেয়ে basic method। একটা single input দিলে synchronously একটা single output ফেরত দেয়।

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("'{topic}' নিয়ে একটা মজার লাইন লেখো")
model = ChatOpenAI()
parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"topic": "বিড়াল"})
print(result)
```

এখানে চেইনটা সম্পূর্ণ শেষ না হওয়া পর্যন্ত কোড অপেক্ষা করে, শেষে পুরো result একসাথে পাওয়া যায়।

## batch — একাধিক input একসাথে

একই input অনেকগুলোর জন্য একসাথে চালাতে হলে loop-এ `invoke` না করে `batch()` ব্যবহার করা ভালো। LangChain ভেতরে ভেতরে এগুলো parallel-এ (থ্রেড/async দিয়ে) চালায়, ফলে speed অনেক বেশি।

```python
results = chain.batch([
    {"topic": "বিড়াল"},
    {"topic": "কুকুর"},
    {"topic": "পাখি"},
])
# results একটা list, প্রতিটা input-এর জন্য একটা output
```

## stream — token/chunk আকারে output

LLM সাধারণত token-by-token output তৈরি করে। পুরো response শেষ হওয়া পর্যন্ত অপেক্ষা না করে `stream()` দিয়ে সেই chunk গুলো আসার সাথে সাথেই দেখানো যায় (যেমন ChatGPT-এর typing effect)।

```python
for chunk in chain.stream({"topic": "বিড়াল"}):
    print(chunk, end="", flush=True)
```

এটা UX-এর জন্য খুব গুরুত্বপূর্ণ — user response আসার জন্য একদমে অপেক্ষা না করে আস্তে আস্তে read করতে পারে।

---

## RunnableParallel — একসাথে একাধিক কাজ চালানো

`RunnableParallel` একই input একাধিক Runnable-এ একসাথে (parallel-এ) পাঠায়, এবং প্রতিটার output একটা dictionary-তে key দিয়ে সাজিয়ে দেয়।

```python
from langchain_core.runnables import RunnableParallel

joke_chain = ChatPromptTemplate.from_template("{topic} নিয়ে একটা জোক") | model | parser
poem_chain = ChatPromptTemplate.from_template("{topic} নিয়ে একটা ছোট কবিতা") | model | parser

combined = RunnableParallel(joke=joke_chain, poem=poem_chain)

result = combined.invoke({"topic": "চাঁদ"})
# result = {"joke": "...", "poem": "..."}
```

চেইনের মধ্যে plain dict ব্যবহার করলেও LangChain সেটাকে অটোমেটিক `RunnableParallel`-এ convert করে নেয়:

```python
chain = {"joke": joke_chain, "poem": poem_chain} | combine_prompt | model
```

মূল সুবিধা হলো — একাধিক স্বাধীন কাজ (যেমন retrieval + summarization) sequential না করে parallel-এ চালিয়ে latency কমানো যায়।

## RunnablePassthrough — input অপরিবর্তিত পাঠানো

RAG (Retrieval-Augmented Generation) চেইনে খুবই common সমস্যা: retriever-এ যাওয়ার সময় শুধু "question" লাগে retrieval করার জন্য, কিন্তু prompt-এ আবার সেই original question-টাও লাগে। `RunnablePassthrough` দিয়ে input-কে কোনো পরিবর্তন না করেই পরের ধাপে পাঠিয়ে দেওয়া যায়।

```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | model
    | parser
)

rag_chain.invoke("ঢাকার ইতিহাস কী?")
```

এখানে `retriever` ইনপুট স্ট্রিং নিয়ে relevant document খুঁজে আনছে (`context` হিসেবে), আর `RunnablePassthrough()` সেই একই স্ট্রিংটা অপরিবর্তিতভাবে `question` key-তে বসিয়ে দিচ্ছে।

`.assign()` দিয়ে existing input dict-এ নতুন key যুক্তও করা যায় (পুরোনো data রেখে দিয়েই):

```python
chain = RunnablePassthrough.assign(context=retriever)
# input: {"question": "..."}  →  output: {"question": "...", "context": [...]}
```

## RunnableBranch — কন্ডিশন অনুযায়ী রুটিং

`RunnableBranch` হলো চেইনের জন্য if/elif/else। input অনুযায়ী কোন condition true হচ্ছে, সেটা চেক করে সেই অনুযায়ী আলাদা আলাদা sub-chain চালায়।

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (lambda x: "code" in x["topic"].lower(), code_chain),
    (lambda x: "history" in x["topic"].lower(), history_chain),
    general_chain  # কোনো condition match না হলে এটা default
)

branch.invoke({"topic": "python code নিয়ে প্রশ্ন"})  # → code_chain চলবে
```

প্রতিটা tuple-এ `(condition_function, runnable)` — condition গুলো উপর থেকে নিচে চেক হয়, প্রথম যেটা `True` হয় সেই Runnable চলে। কোনোটাই match না হলে শেষে দেওয়া default Runnable চলে।

---

## সব মিলিয়ে এক উদাহরণ

```python
classify_chain = RunnableParallel(
    topic=RunnablePassthrough(),
    language=lang_detect_chain,
)

full_chain = (
    classify_chain
    | RunnableBranch(
        (lambda x: x["language"] == "bn", bangla_response_chain),
        english_response_chain,
    )
)

full_chain.invoke({"topic": "What is LCEL?"})
```

এখানে প্রথমে `RunnableParallel` দিয়ে ভাষা detect করা হচ্ছে, তারপর `RunnableBranch` সেই ভাষা অনুযায়ী সঠিক response chain-এ পাঠাচ্ছে।

কোনো একটা অংশ নিয়ে আরও গভীরে যেতে চাইলে (যেমন `RunnableLambda`, error handling, বা async variant গুলো) বলো — সেটাও explain করে দিচ্ছি।