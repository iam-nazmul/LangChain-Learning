
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



---

# RunnableLambda

`RunnableLambda` দিয়ে কোনো সাধারণ Python function (বা lambda) কে একটা Runnable-এ পরিণত করা যায়, যাতে সেটাকে LCEL chain-এর ভেতরে `|` অপারেটর দিয়ে অন্য component-গুলোর সাথে বসানো যায়।

আসল সমস্যাটা হলো — chain-এর মধ্যে যদি custom logic (যেমন string manipulation, কোনো calculation, বা data transform) ঢোকাতে চাও, plain Python function সরাসরি `|` operator support করে না। `RunnableLambda` সেই function-টাকে wrap করে দেয়, ফলে সেটা অন্য সব Runnable (prompt, model, parser) এর মতই `invoke`, `batch`, `stream` করতে পারে।

```python
from langchain_core.runnables import RunnableLambda

def word_count(text: str) -> int:
    return len(text.split())

counter = RunnableLambda(word_count)
counter.invoke("আমি ভালো আছি")   # → 3
```

---

## Chain-এর ভেতরে ব্যবহার

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

prompt = ChatPromptTemplate.from_template("{topic} নিয়ে একটা ছোট প্যারাগ্রাফ লেখো")
model = ChatOpenAI()
parser = StrOutputParser()

def to_uppercase(text: str) -> str:
    return text.upper()

chain = prompt | model | parser | RunnableLambda(to_uppercase)

chain.invoke({"topic": "নদী"})
```

এখানে model-এর response আসার পর সেটাকে `to_uppercase` function দিয়ে post-process করা হলো।

### স্বয়ংক্রিয় coercion

LCEL chain-এ `|` দিয়ে যদি plain function বসানো হয়, LangChain নিজেই সেটাকে `RunnableLambda`-এ convert করে নেয় — explicit wrap না করলেও চলে:

```python
chain = prompt | model | parser | to_uppercase   # to_uppercase নিজেই auto-wrap হয়ে যাবে
```

তবে explicit ভাবে `RunnableLambda(...)` লেখা ভালো practice, কারণ এতে কোডটা পড়তে স্পষ্ট হয় এবং কিছু edge case-এ (যেমন type hints না থাকলে) auto-coercion ঠিকভাবে কাজ না করার সম্ভাবনা কমে।

---

## Dict input নিয়ে কাজ করা

Chain-এর মাঝে data সাধারণত dictionary আকারে থাকে, তাই function-টাকে সেই dict গ্রহণ করতে হয়:

```python
def format_question(data: dict) -> str:
    return f"প্রশ্ন: {data['question']} (ভাষা: {data['language']})"

chain = RunnableLambda(format_question) | prompt | model | parser
```

## Lambda এক্সপ্রেশন সরাসরি

ছোট-খাটো transform-এর জন্য সরাসরি `lambda` ও ব্যবহার করা যায়:

```python
chain = prompt | model | parser | RunnableLambda(lambda x: x.strip().lower())
```

---

## একটা গুরুত্বপূর্ণ সীমাবদ্ধতা: streaming

`RunnableLambda` দিয়ে wrap করা সাধারণ function **streaming support করে না** by default — অর্থাৎ chain-এ যদি এটা ব্যবহার করো, তাহলে আগের ধাপ থেকে আসা chunk গুলো এই function-এ একসাথে (পুরো input হিসেবে) আসবে, token-by-token আসবে না। কারণ function নিজে জানে না কীভাবে partial input handle করতে হয়।

Streaming বজায় রাখতে চাইলে generator function ব্যবহার করতে হয়:

```python
def stream_transform(chunks):
    for chunk in chunks:
        yield chunk.upper()

chain = prompt | model | parser | RunnableLambda(stream_transform)
```

এখানে function input হিসেবে একটা iterator নেয় এবং chunk-by-chunk yield করে, ফলে streaming behavior ঠিক থাকে।

---

## RunnableLambda বনাম `.assign()` / inline dict

ছোট transform-এর জন্য অনেক সময় `RunnablePassthrough.assign()`-এর ভেতরেও `RunnableLambda` ঢোকানো হয়:

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough.assign(
    word_count=RunnableLambda(lambda x: len(x["text"].split()))
)

chain.invoke({"text": "এটা একটা পরীক্ষা বাক্য"})
# → {"text": "এটা একটা পরীক্ষা বাক্য", "word_count": 4}
```

এভাবে original input অপরিবর্তিত রেখে নতুন একটা computed key যুক্ত করা যায় — অনেকটা `RunnableParallel`-এর মতই, কিন্তু existing keys preserve করে।

---

## কখন ব্যবহার করবে

- **Pre-processing**: model-এ পাঠানোর আগে input format/clean করতে
- **Post-processing**: model output থেকে কিছু extract বা reformat করতে (যেমন JSON parse, regex দিয়ে filter)
- **Conditional logic-এর ছোট অংশ**: `RunnableBranch`-এর condition function হিসেবেও আসলে এটাই কাজ করে ভেতরে ভেতরে
- **Debugging**: মাঝে একটা `RunnableLambda(lambda x: print(x) or x)` বসিয়ে intermediate value দেখা

কোনো নির্দিষ্ট use-case নিয়ে (যেমন error handling এর জন্য `with_fallbacks`, বা retry logic) আরও জানতে চাইলে বলো।


---


# Error Handling

LCEL chain-এ error handle করার মূলত তিনটা প্রধান টুল আছে: `with_retry`, `with_fallbacks`, আর `RunnableLambda`-এর ভেতরে try/except।

## with_retry — ব্যর্থ হলে আবার চেষ্টা করা

API rate limit, network glitch, বা timeout-এর মতো transient error-এর জন্য পুরো call আবার চেষ্টা করানো যায়।

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

resilient_model = model.with_retry(
    stop_after_attempt=3,          # সর্বোচ্চ ৩ বার চেষ্টা
    wait_exponential_jitter=True,  # প্রতি বার অপেক্ষার সময় বাড়বে (exponential backoff)
)

chain = prompt | resilient_model | parser
chain.invoke({"topic": "বৃষ্টি"})
```

এখানে যদি প্রথম call ব্যর্থ হয়, LangChain নিজে নিজে আবার চেষ্টা করবে (jitter দিয়ে wait করে যাতে একসাথে অনেক request retry করে server-কে আরও চাপ না দেয়)। ৩ বারের পরেও ব্যর্থ হলে exception raise হবে।

## with_fallbacks — primary ব্যর্থ হলে backup চালানো

যদি একটা model/chain সম্পূর্ণ ব্যর্থ হয় (যেমন downtime, বা error যেটা retry করেও ঠিক হয় না), তখন সম্পূর্ণ ভিন্ন একটা backup Runnable চালানো যায়।

```python
primary_model = ChatOpenAI(model="gpt-4o")
backup_model = ChatOpenAI(model="gpt-3.5-turbo")  # সস্তা/দ্রুত fallback

model_with_fallback = primary_model.with_fallbacks([backup_model])

chain = prompt | model_with_fallback | parser
```

একাধিক fallback chain করেও দেওয়া যায় — প্রথমটা fail করলে দ্বিতীয়টা, সেটাও fail করলে তৃতীয়টা, এভাবে।

```python
chain_with_fallback = primary_chain.with_fallbacks(
    [backup_chain_1, backup_chain_2]
)
```

`with_retry` আর `with_fallbacks` একসাথেও বসানো যায় — আগে retry, retry সব শেষ হয়ে গেলে fallback:

```python
robust_model = model.with_retry(stop_after_attempt=2).with_fallbacks([backup_model])
```

## RunnableLambda-তে নিজে try/except

custom error handling logic দরকার হলে (যেমন error হলে একটা default value ফেরত দেওয়া) `RunnableLambda` দিয়ে নিজে handle করা যায়।

```python
from langchain_core.runnables import RunnableLambda

def safe_parse(text: str) -> dict:
    try:
        import json
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "parse failed", "raw": text}

chain = prompt | model | parser | RunnableLambda(safe_parse)
```

## batch-এ partial failure handle করা

`batch()` দিয়ে অনেকগুলো input চালালে, default-এ একটা ব্যর্থ হলে পুরো batch exception ছুঁড়ে দেয়। `return_exceptions=True` দিলে বাকি input গুলোর result পাওয়া যায়, আর যেটা fail করেছে সেখানে exception object বসে থাকে।

```python
results = chain.batch(
    [{"topic": "বিড়াল"}, {"topic": "কুকুর"}, {"topic": ""}],
    return_exceptions=True,
)

for r in results:
    if isinstance(r, Exception):
        print("ব্যর্থ:", r)
    else:
        print("সফল:", r)
```

---

# Async Variants

LangChain-এর প্রতিটা sync method-এর একটা async ভার্সন আছে — নাম শুরু হয় `a` দিয়ে।

| Sync | Async |
|---|---|
| `invoke` | `ainvoke` |
| `batch` | `abatch` |
| `stream` | `astream` |
| (নাই) | `astream_events` |

```python
import asyncio

async def main():
    result = await chain.ainvoke({"topic": "সূর্য"})
    print(result)

    results = await chain.abatch([
        {"topic": "বিড়াল"},
        {"topic": "কুকুর"},
    ])

    async for chunk in chain.astream({"topic": "চাঁদ"}):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## কেন async ব্যবহার করবে

মূল সুবিধা concurrency — একাধিক independent LLM call একসাথে চালাতে চাইলে (যেমন web server-এ একসাথে অনেক user request আসছে), async দিয়ে CPU/thread কম খরচ করেই বেশি request handle করা যায়।

```python
async def process_many(topics: list[str]):
    tasks = [chain.ainvoke({"topic": t}) for t in topics]
    return await asyncio.gather(*tasks)

results = asyncio.run(process_many(["AI", "বাংলাদেশ", "ক্রিকেট"]))
```

এখানে `asyncio.gather` দিয়ে সবগুলো call একসাথে শুরু হচ্ছে এবং সবার শেষ হওয়ার জন্য একবারে অপেক্ষা করা হচ্ছে — `abatch` ভেতরে ভেতরে কাছাকাছি এটাই করে, কিন্তু নিজে manual concurrency লিখলে আরও বেশি control পাওয়া যায় (যেমন rate-limit করে চালানো)।

## astream_events — চেইনের প্রতিটা ধাপের ইভেন্ট দেখা

জটিল চেইনে (একাধিক sub-chain, tool call, retriever) ঠিক কোন ধাপে কী ঘটছে সেটা track করতে `astream_events` ব্যবহার হয়। এটা প্রতিটা component-এর start/end ইভেন্ট ফেরত দেয়, শুধু final output না।

```python
async def trace():
    async for event in chain.astream_events({"topic": "ইতিহাস"}, version="v2"):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="")
        elif kind == "on_chain_start":
            print(f"\n[শুরু হলো: {event['name']}]")

asyncio.run(trace())
```

UI-তে যদি দেখাতে চাও যে "এখন retriever চলছে", "এখন model token generate করছে" — এই granular visibility `astream_events` দিয়েই সম্ভব।

## কোন কোন component async support করে

LangChain-এর built-in সব component (prompt, model, parser, retriever) এর async ভার্সন আছে। কিন্তু নিজের লেখা `RunnableLambda` যদি plain (sync) function হয়, LangChain স্বয়ংক্রিয়ভাবে সেটাকে thread-এ চালিয়ে async context-এ ব্যবহার করার চেষ্টা করে — কাজ করে, কিন্তু true async না। সত্যিকারের non-blocking behavior চাইলে নিজে `async def` function লিখে `RunnableLambda` কে দুটো function (sync + async ভার্সন) দেওয়া যায়:

```python
def sync_fn(x):
    return x.upper()

async def async_fn(x):
    # imagine কোনো async I/O এখানে
    return x.upper()

dual_runnable = RunnableLambda(sync_fn, afunc=async_fn)
```

এতে sync context-এ `sync_fn` চলবে, async context-এ (`ainvoke`/`astream`) আসল async function `async_fn` চলবে — কোনো thread-pool overhead লাগবে না।

---

কিছু নির্দিষ্ট দিক নিয়ে আরও গভীরে যাওয়া যায়, যেমন `RunnableConfig` দিয়ে timeout/tag/metadata pass করা, বা LangSmith-এর সাথে integration করে error trace দেখা — চাইলে বলো।


---

## LCEL (LangChain Expression Language) কী?

**LCEL** হলো LangChain-এর একটি declarative syntax, যা ব্যবহার করে বিভিন্ন LLM, Prompt, Retriever, Parser ইত্যাদি একসাথে chain আকারে যুক্ত করা যায়।

ধরুন:

```python
chain = prompt | llm | output_parser
```

এখানে `|` অপারেটর ব্যবহার করে এক component-এর output পরের component-এর input হিসেবে যাচ্ছে।

---

# ১. Runnable কী?

LangChain-এ প্রায় সব component-ই **Runnable**।

যেমন:

* PromptTemplate
* ChatModel
* OutputParser
* Retriever
* Custom Function

সবগুলোই Runnable interface follow করে।

Runnable-এর মূল কাজ:

```
Input → Process → Output
```

---

# ২. invoke()

একটি input দিয়ে chain একবার execute করার জন্য `invoke()` ব্যবহার করা হয়।

### Example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()

result = llm.invoke("বাংলাদেশের রাজধানী কোথায়?")
print(result.content)
```

### Flow

```
Input
  ↓
invoke()
  ↓
LLM
  ↓
Output
```

---

## LCEL Example

```python
chain = prompt | llm

response = chain.invoke({
    "topic": "Python"
})
```

---

# ৩. batch()

একাধিক input একসাথে process করার জন্য।

যখন ১০০টা query একবারে চালাতে হবে তখন loop না দিয়ে batch ব্যবহার করা যায়।

### Example

```python
questions = [
    "What is Python?",
    "What is Django?",
    "What is FastAPI?"
]

results = llm.batch(questions)

for r in results:
    print(r.content)
```

---

### Flow

```
Question 1 ─┐
Question 2 ─┼── batch()
Question 3 ─┘
              ↓
           Outputs
```

---

# ৪. stream()

Response আসার সাথে সাথে token-by-token পাওয়া যায়।

ChatGPT typing effect এর মতো।

### Example

```python
for chunk in llm.stream("Explain Python"):
    print(chunk.content, end="")
```

---

### Flow

```
Input
  ↓
LLM
  ↓
Token 1
Token 2
Token 3
Token 4
...
```

---

# RunnableParallel

একই input দিয়ে একাধিক Runnable parallel-এ execute করে।

---

## Example

```python
from langchain_core.runnables import RunnableParallel

chain = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
    sentiment=sentiment_chain,
)

result = chain.invoke("আজকের আবহাওয়া সুন্দর")
```

Output:

```python
{
    "summary": "...",
    "keywords": "...",
    "sentiment": "positive"
}
```

---

### Diagram

```
                    ┌── Summary Chain
Input ──────────────┤
                    ├── Keyword Chain
                    │
                    └── Sentiment Chain
                          ↓
                    Combined Result
```

---

## Practical Use Case

একটি article থেকে একসাথে:

* Summary
* Keywords
* Sentiment
* Category

generate করতে।

---

# RunnablePassthrough

Input-কে modify না করে সামনে পাঠিয়ে দেয়।

---

## Example

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough()

result = chain.invoke("Hello")
```

Output:

```python
"Hello"
```

---

## Real Example

```python
chain = {
    "question": RunnablePassthrough(),
    "answer": llm
}
```

Input:

```python
"What is Python?"
```

Output:

```python
{
    "question": "What is Python?",
    "answer": "Python is ..."
}
```

---

### Diagram

```
Input
  │
  ├──────────► Question
  │
  └──────────► LLM
                 ↓
               Answer
```

---

## Use Case

RAG Application-এ:

```python
{
    "question": RunnablePassthrough(),
    "context": retriever
}
```

একই question retriever এবং LLM উভয়ের কাছে পাঠাতে।

---

# RunnableBranch

Condition অনুযায়ী different chain execute করে।

Python-এর `if-else` এর মতো।

---

## Example

```python
from langchain_core.runnables import RunnableBranch

branch = RunnableBranch(
    (
        lambda x: "python" in x.lower(),
        python_chain
    ),
    (
        lambda x: "django" in x.lower(),
        django_chain
    ),
    default_chain
)
```

---

Input:

```python
branch.invoke("Tell me about Python")
```

Run করবে:

```python
python_chain
```

---

Input:

```python
branch.invoke("Tell me about Django")
```

Run করবে:

```python
django_chain
```

---

### Diagram

```
                ┌─ Python Chain
Input ─ Check ──┤
                │
                ├─ Django Chain
                │
                └─ Default Chain
```

---

## Practical Use Case

একটি AI Assistant:

```python
যদি:
    Billing Question → Billing Chain

যদি:
    Technical Question → Technical Chain

যদি:
    Sales Question → Sales Chain

নাহলে:
    General Assistant Chain
```

---

# সবকিছু একসাথে

ধরুন আপনি একটি RAG Chatbot বানাচ্ছেন:

```python
chain = (
    {
        "question": RunnablePassthrough(),
        "context": retriever
    }
    | prompt
    | llm
)
```

Flow:

```
User Question
      │
      ├────► Retriever
      │          ↓
      │      Context
      │
      └────► Original Question
                    ↓
                 Prompt
                    ↓
                   LLM
                    ↓
                 Answer
```

---

## সংক্ষেপে

| Component             | কাজ                                         |
| --------------------- | ------------------------------------------- |
| `invoke()`            | একবারে একটি input execute                   |
| `batch()`             | অনেক input একসাথে execute                   |
| `stream()`            | token-by-token output                       |
| `RunnableParallel`    | একই input দিয়ে একাধিক chain parallel চালানো |
| `RunnablePassthrough` | input অপরিবর্তিত রেখে forward করা           |
| `RunnableBranch`      | condition অনুযায়ী ভিন্ন chain চালানো        |
| `LCEL ( \| )`         | Runnable গুলো chain আকারে connect করা       |

LCEL-এর সবচেয়ে বড় সুবিধা হলো আপনি খুব কম কোডে জটিল AI workflow (RAG, Agent, Multi-step Pipeline, Router, Parallel Processing) তৈরি করতে পারেন।
