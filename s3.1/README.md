# এজেন্ট (Agent) — SPEC

## এজেন্ট কী?

এজেন্ট হলো টুল ব্যবহার করা একটি AI, কিন্তু চেইন (chain) থেকে এটা মৌলিকভাবে ভিন্ন।

- **চেইন**: একরৈখিক (linear)। ধাপগুলো আগে থেকেই নির্দিষ্ট — শুরু থেকে শেষ পর্যন্ত একই পথ ধরে চলে। কোন ধাপের পর কোনটা আসবে, সেটা কোড লেখার সময়েই ঠিক করা থাকে।
- **এজেন্ট**: মডেল নিজেই "চিন্তা" করে সিদ্ধান্ত নেয় — কোন টুল ব্যবহার করবে, কখন করবে, এবং ফলাফল দেখার পর পরবর্তী পদক্ষেপ কী হবে। এই *reason → act → observe* লুপ চলতে থাকে যতক্ষণ না কাজ শেষ হয়। অর্থাৎ পথ আগে থেকে নির্ধারিত নয়; মডেল নিজেই পথ তৈরি করে।

এই কারণে এজেন্ট বেশি নমনীয়, কিন্তু একই সাথে অনির্দেশযোগ্য (less predictable) — তাই এজেন্ট তৈরির সময় guardrails, error handling, এবং structured output নিয়ন্ত্রণ খুব গুরুত্বপূর্ণ হয়ে ওঠে।

---

## যা শিখবেন

1. **Tools** — মডেলকে দেওয়া ফাংশন/ক্ষমতা (ওয়েব সার্চ, ক্যালকুলেটর, API কল, নিজের লেখা Python ফাংশন)।
2. **`create_agent`** — high-level API দিয়ে দ্রুত এজেন্ট তৈরি (LangGraph-এর ওপর নির্মিত)।
3. **Agent loop** — reason → act (tool call) → observe → repeat।
4. **Middleware** — এজেন্টের আচরণ কাস্টমাইজ করা, guardrails যোগ করা, এরর সামলানো, PII সুরক্ষা ইত্যাদি।
5. **Structured output** — Pydantic schema দিয়ে এজেন্টের কাছ থেকে নির্ভরযোগ্য কাঠামোবদ্ধ উত্তর পাওয়া।

---

## ১. Tools

Tool হলো এমন একটি ফাংশন যা মডেলকে বাইরের জগতের সাথে যোগাযোগ করার ক্ষমতা দেয় — যেমন তথ্য খুঁজে আনা, হিসাব করা, বা কোনো সিস্টেমে অ্যাকশন নেওয়া। প্রতিটি টুলের একটি নাম, একটি বর্ণনা (docstring), এবং ইনপুট/আউটপুট টাইপ থাকে — মডেল এই বর্ণনা দেখেই বুঝতে পারে কখন কোন টুল ব্যবহার করতে হবে।

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """একটি শহরের বর্তমান আবহাওয়া জানায়।"""
    # বাস্তবে এখানে একটি weather API কল হবে
    return f"{city}-এ আজ আবহাওয়া রৌদ্রোজ্জ্বল, তাপমাত্রা ৩২°সে।"

@tool
def calculator(expression: str) -> str:
    """একটি গাণিতিক এক্সপ্রেশন হিসাব করে।"""
    return str(eval(expression))
```

ভালো টুল ডিজাইনের নীতি:
- নামকরণ স্পষ্ট এবং একক-উদ্দেশ্যভিত্তিক হওয়া উচিত।
- Docstring/বর্ণনা এমনভাবে লেখা উচিত যেন মডেল বুঝতে পারে *কখন* এটা ব্যবহার করবে।
- ইনপুট/আউটপুট টাইপ স্পষ্টভাবে সংজ্ঞায়িত (type-annotated) হওয়া উচিত, যাতে মডেল সঠিক আর্গুমেন্ট পাঠাতে পারে।

---

## ২. `create_agent`

`create_agent` একটি high-level API যা LangGraph-এর ওপর তৈরি — এটি দিয়ে মাত্র কয়েক লাইনে একটি সম্পূর্ণ কার্যকরী এজেন্ট তৈরি করা যায়, অথচ ভেতরে LangGraph-এর সম্পূর্ণ state-machine ভিত্তিক এক্সিকিউশন ইঞ্জিন থাকে (যার ফলে streaming, persistence, human-in-the-loop ইত্যাদি সুবিধা স্বয়ংক্রিয়ভাবে পাওয়া যায়)।

```python
from langchain.agents import create_agent

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather, calculator],
    system_prompt="আপনি একজন সহায়ক সহকারী। প্রয়োজনে টুল ব্যবহার করুন।",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "ঢাকার আবহাওয়া কেমন, আর ১৫*২৩ কত?"}]
})

print(result["messages"][-1].content)
```

---

## ৩. Agent Loop

`create_agent`-এর ভেতরে যে লুপ চলে, তা মূলত তিনটি ধাপের পুনরাবৃত্তি:

```
┌─────────────┐     ┌────────────┐     ┌───────────┐
│   Reason    │ ──▶ │    Act     │ ──▶ │  Observe  │
│ (মডেল চিন্তা │     │(tool call) │     │ (ফলাফল    │
│  করে সিদ্ধান্ত│     │            │     │  বিশ্লেষণ)│
│  নেয়)       │     │            │     │           │
└─────────────┘     └────────────┘     └───────────┘
       ▲                                     │
       └─────────────────────────────────────┘
              (কাজ শেষ না হওয়া পর্যন্ত পুনরাবৃত্তি)
```

1. **Reason** — মডেল বর্তমান কথোপকথন ও প্রসঙ্গ দেখে চিন্তা করে পরবর্তী পদক্ষেপ কী হবে।
2. **Act** — প্রয়োজন হলে একটি টুল কল করে (একাধিক টুল সমান্তরালেও কল হতে পারে)।
3. **Observe** — টুলের ফলাফল কথোপকথনে যুক্ত হয়, মডেল সেটা দেখে আবার চিন্তা করে।

এই লুপ থামে যখন মডেল সিদ্ধান্ত নেয় যে আর কোনো টুল প্রয়োজন নেই এবং একটি চূড়ান্ত উত্তর দেওয়া যায়। এই কারণেই এজেন্ট চেইনের চেয়ে ভিন্ন — পথ আগে থেকে নির্ধারিত নয়, প্রতিটি ধাপে মডেল নিজেই সিদ্ধান্ত নেয়।

---

## ৪. Middleware

Middleware হলো ১.০-এর একটি নতুন ধারণা, যা দিয়ে agent loop-এর বিভিন্ন পয়েন্টে (মডেল কল করার আগে/পরে, টুল কল করার আগে/পরে) কাস্টম লজিক ইনজেক্ট করা যায়। এর ব্যবহারিক প্রয়োগ:

- **Guardrails** — নির্দিষ্ট কিছু টুল বা আউটপুট ব্লক করা।
- **Error handling** — টুল ব্যর্থ হলে গ্রেসফুলি সামলানো, retry করা।
- **PII সুরক্ষা** — ইনপুট/আউটপুট থেকে সংবেদনশীল তথ্য (ফোন নম্বর, ইমেইল ইত্যাদি) রিডাক্ট করা।
- **Logging/Observability** — প্রতিটি ধাপ লগ করা বা মনিটরিং টুলে পাঠানো।

```python
from langchain.agents.middleware import AgentMiddleware

class PIIRedactionMiddleware(AgentMiddleware):
    def before_model(self, state):
        # মডেলে পাঠানোর আগে সংবেদনশীল তথ্য রিডাক্ট করা
        for msg in state["messages"]:
            msg.content = redact_pii(msg.content)
        return state

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather, calculator],
    middleware=[PIIRedactionMiddleware()],
)
```

Middleware-কে স্তরে স্তরে (stack) সাজানো যায়, ফলে একাধিক নিয়ন্ত্রণ একসাথে প্রয়োগ করা সম্ভব — যেমন একই এজেন্টে PII রিডাকশন, rate-limiting, এবং logging middleware একসাথে থাকতে পারে।

---

## ৫. Structured Output

এজেন্টের চূড়ান্ত উত্তর প্রায়ই ফ্রি-টেক্সট না হয়ে একটি নির্দিষ্ট কাঠামোতে (JSON/object) দরকার হয় — যেমন ডাউনস্ট্রিম সিস্টেমে ব্যবহারের জন্য। Pydantic schema দিয়ে এটা নির্ভরযোগ্যভাবে করা যায়:

```python
from pydantic import BaseModel, Field

class WeatherReport(BaseModel):
    city: str = Field(description="শহরের নাম")
    temperature_celsius: float = Field(description="তাপমাত্রা (সেলসিয়াস)")
    condition: str = Field(description="আবহাওয়ার অবস্থা, যেমন 'রৌদ্রোজ্জ্বল'")

agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather],
    response_format=WeatherReport,
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "ঢাকার আবহাওয়া রিপোর্ট দাও"}]
})

report: WeatherReport = result["structured_response"]
print(report.city, report.temperature_celsius, report.condition)
```

এতে মডেল টুল ব্যবহার করে তথ্য সংগ্রহ করার পরেও নিশ্চিত করে যে চূড়ান্ত আউটপুট নির্দিষ্ট schema মেনে চলে — validation error বা অসম্পূর্ণ ফিল্ডের ঝুঁকি কমে যায়।

---

## একটি সিম্পল টুল-ব্যবহারকারী এজেন্ট (সম্পূর্ণ উদাহরণ)

নিচে উপরের সব ধারণা একত্র করে একটি সম্পূর্ণ, কার্যকর উদাহরণ দেওয়া হলো:

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents.middleware import AgentMiddleware
from pydantic import BaseModel, Field


# ১. Tools সংজ্ঞায়িত করা
@tool
def get_weather(city: str) -> str:
    """একটি শহরের বর্তমান আবহাওয়া জানায়।"""
    fake_data = {"ঢাকা": (32, "রৌদ্রোজ্জ্বল"), "চট্টগ্রাম": (29, "মেঘলা")}
    temp, condition = fake_data.get(city, (30, "অজানা"))
    return f"{city}: {temp}°সে, {condition}"


@tool
def calculator(expression: str) -> str:
    """একটি সরল গাণিতিক এক্সপ্রেশন হিসাব করে।"""
    return str(eval(expression))


# ২. Middleware — প্রতিটি ধাপ লগ করার জন্য
class LoggingMiddleware(AgentMiddleware):
    def after_model(self, state):
        last = state["messages"][-1]
        print(f"[LOG] মডেলের সিদ্ধান্ত: {last.content[:80]}...")
        return state


# ৩. Structured output schema
class WeatherReport(BaseModel):
    city: str = Field(description="শহরের নাম")
    temperature_celsius: float
    condition: str


# ৪. এজেন্ট তৈরি
agent = create_agent(
    model="claude-sonnet-4-6",
    tools=[get_weather, calculator],
    middleware=[LoggingMiddleware()],
    system_prompt="আপনি একজন সহায়ক সহকারী যিনি প্রয়োজনে টুল ব্যবহার করেন।",
    response_format=WeatherReport,
)

# ৫. এজেন্ট চালানো — reason → act → observe লুপ স্বয়ংক্রিয়ভাবে চলবে
result = agent.invoke({
    "messages": [{"role": "user", "content": "ঢাকার আবহাওয়া রিপোর্ট দাও।"}]
})

report: WeatherReport = result["structured_response"]
print(f"\nচূড়ান্ত রিপোর্ট: {report.city} — {report.temperature_celsius}°সে, {report.condition}")
```

এই উদাহরণে যা ঘটছে:
1. ইউজার প্রশ্ন করলে মডেল প্রথমে **reason** করে বুঝে নেয় আবহাওয়ার তথ্য দরকার।
2. এরপর **act** ধাপে `get_weather` টুল কল করে।
3. `LoggingMiddleware`-এর `after_model` হুক প্রতিটি ধাপে সিদ্ধান্ত লগ করে।
4. ফলাফল **observe** করে মডেল বুঝে নেয় আর কোনো টুল দরকার নেই।
5. চূড়ান্ত উত্তর `WeatherReport` schema অনুযায়ী কাঠামোবদ্ধ আকারে ফেরত আসে।

---
---
---
---
