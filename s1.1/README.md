Chat Models এবং Messages নিয়ে বাংলায় ব্যাখ্যা দিচ্ছি — এটি LangChain ফ্রেমওয়ার্কের একটি মৌলিক কনসেপ্ট।

## Chat Models কী?

আধুনিক LLM (যেমন GPT, Claude) গুলো সাধারণ টেক্সট-ইন-টেক্সট-আউট মডেল না — এরা **conversation-based** বা কথোপকথন-ভিত্তিক। মানে এরা একটা single string ইনপুট নেয় না, বরং **messages-এর একটা লিস্ট** নেয়, যেখানে প্রতিটি মেসেজের একটা **role** (ভূমিকা) এবং **content** (বিষয়বস্তু) থাকে।

LangChain-এ এই role-ভিত্তিক মেসেজগুলো রিপ্রেজেন্ট করার জন্য তিনটি মূল ক্লাস আছে।

## ১. `SystemMessage`

এটা মডেলকে **নির্দেশনা বা প্রসঙ্গ (context)** দেওয়ার জন্য ব্যবহৃত হয় — কথোপকথন শুরুর আগেই।

- মডেলের **আচরণ, পার্সোনা, নিয়ম** নির্ধারণ করে
- ইউজার বা AI কথা বলার আগেই এটা সেট করা থাকে
- সাধারণত conversation-এর প্রথম মেসেজ হিসেবে থাকে

```python
from langchain_core.messages import SystemMessage

system_msg = SystemMessage(content="তুমি একজন সহায়ক বাংলা শিক্ষক। সবসময় সহজ ভাষায় উত্তর দেবে।")
```

**উদাহরণ ব্যবহার:** "তুমি একজন প্রফেশনাল ডাক্তার", "শুধু JSON ফরম্যাটে উত্তর দাও", "তুমি একটা পাইরেটের মতো কথা বলবে" — এই ধরনের instruction এখানে যায়।

## ২. `HumanMessage`

এটা **ইউজারের পক্ষ থেকে পাঠানো মেসেজ** রিপ্রেজেন্ট করে — মানুষ যা টাইপ করে বা বলে।

```python
from langchain_core.messages import HumanMessage

human_msg = HumanMessage(content="ঢাকার রাজধানী কোথায়?")
```

- এটা real user input বা প্রোগ্রাম থেকে পাঠানো query হতে পারে
- Conversation history-তে এটা "প্রশ্ন" বা "request" পার্ট

## ৩. `AIMessage`

এটা **মডেল (AI) যা রেসপন্স দিয়েছে** তা রিপ্রেজেন্ট করে।

```python
from langchain_core.messages import AIMessage

ai_msg = AIMessage(content="ঢাকা নিজেই বাংলাদেশের রাজধানী।")
```

- এটা মডেলের আউটপুট স্টোর করে
- Multi-turn conversation-এ আগের AI উত্তরগুলো এখানে রাখা হয়, যাতে মডেল context বুঝতে পারে
- কখনো কখনো `tool_calls` ও এর সাথে attach থাকতে পারে (যদি মডেল কোনো tool call করে)

## সব একসাথে — একটা পূর্ণ উদাহরণ

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o")

messages = [
    SystemMessage(content="তুমি একজন সংক্ষিপ্ত উত্তরদাতা। এক লাইনে উত্তর দাও।"),
    HumanMessage(content="পানির রাসায়নিক সংকেত কী?"),
]

response = model.invoke(messages)
print(response)  # এটা একটা AIMessage অবজেক্ট রিটার্ন করবে
```

মডেল রেসপন্স দেওয়ার পর, এটাকে `messages` লিস্টে যোগ করে দিলে কথোপকথন চালিয়ে যাওয়া যায়:

```python
messages.append(response)  # AIMessage যোগ হলো
messages.append(HumanMessage(content="তাহলে অক্সিজেনের সংকেত কী?"))

response2 = model.invoke(messages)
```

## কেন এই তিনটা আলাদা রাখা জরুরি?

| বিষয় | ব্যাখ্যা |
|---|---|
| **Context আলাদাকরণ** | মডেল বুঝতে পারে কোনটা নির্দেশনা, কোনটা ইউজারের কথা, কোনটা তার নিজের আগের কথা |
| **Conversation history** | Multi-turn চ্যাটে আগের সব exchange ঠিকভাবে ট্র্যাক রাখা যায় |
| **Role-aware প্রসেসিং** | মডেল প্রোভাইডাররা (OpenAI, Anthropic ইত্যাদি) নিজেদের API-তে এই role অনুযায়ী আলাদা ফরম্যাটে রিকোয়েস্ট পাঠায় |
| **Prompt Engineering নিয়ন্ত্রণ** | System message দিয়ে মডেলের behavior নিয়ন্ত্রণ করা সহজ হয়, user input থেকে আলাদা রাখায় |

একটা সহজ মানসিক মডেল: এটাকে একটা স্ক্রিপ্ট/নাটকের মতো ভাবুন —
- **SystemMessage** = পরিচালকের নির্দেশনা (পর্দার আগেই)
- **HumanMessage** = দর্শকের সংলাপ
- **AIMessage** = অভিনেতার (AI) সংলাপ

কোনো নির্দিষ্ট অংশ নিয়ে আরও গভীরে যেতে চান — যেমন `ToolMessage`, streaming response, বা multi-turn memory management?


---


সব কয়টা নিয়েই সংক্ষেপে বলি, তারপর আপনি যেটায় আগ্রহী সেটায় আরও গভীরে যাওয়া যাবে।

## ১. `ToolMessage`

যখন AI কোনো **tool/function কল** করতে চায়, তখন প্রসেসটা একটু ভিন্ন হয় — তিনটা ধাপে চলে:

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """কোনো শহরের আবহাওয়া জানায়।"""
    return f"{city}-এ আজ ৩২°C, রোদ আছে।"

model_with_tools = model.bind_tools([get_weather])

messages = [HumanMessage(content="ঢাকার আবহাওয়া কেমন?")]

# ধাপ ১: মডেল বুঝে যে tool কল লাগবে
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)  # এতে ai_msg.tool_calls থাকবে

# ধাপ ২: আমরা সেই tool বাস্তবে রান করি
for tool_call in ai_msg.tool_calls:
    result = get_weather.invoke(tool_call["args"])
    # ধাপ ৩: ফলাফল ToolMessage হিসেবে যুক্ত করি
    messages.append(ToolMessage(
        content=result,
        tool_call_id=tool_call["id"]  # কোন কলের উত্তর তা ট্র্যাক করার জন্য জরুরি
    ))

# এখন মডেল আবার কল করলে সে tool-এর রেজাল্ট দেখে চূড়ান্ত উত্তর দেবে
final_response = model_with_tools.invoke(messages)
```

`tool_call_id` টা গুরুত্বপূর্ণ — একসাথে একাধিক tool কল হলে কোনটার উত্তর কোনটা, তা মডেলকে বুঝতে সাহায্য করে।

## ২. Streaming Response

পুরো উত্তর একবারে না দিয়ে, **টুকরো টুকরো (chunk)** করে রিয়েল-টাইমে দেখানো যায় — ChatGPT-তে যেমন টাইপ হতে হতে উত্তর আসে।

```python
for chunk in model.stream(messages):
    print(chunk.content, end="", flush=True)
```

প্রতিটা `chunk` একটা `AIMessageChunk` — যেগুলো একসাথে জোড়া দিলে পুরো `AIMessage` হয়:

```python
full_response = None
for chunk in model.stream(messages):
    full_response = chunk if full_response is None else full_response + chunk
    print(chunk.content, end="")

print("\n\nসম্পূর্ণ মেসেজ:", full_response)
```

Async ভার্সনও আছে (`astream`), যা FastAPI বা ওয়েব অ্যাপে real-time UI আপডেটের জন্য বেশি ব্যবহৃত হয়।

## ৩. Multi-turn Memory Management

লম্বা কথোপকথনে সব মেসেজ জমিয়ে রাখলে context window ভরে যায় এবং খরচও বাড়ে। তাই মেসেজ history ম্যানেজ করার কয়েকটা কৌশল আছে:

**ক) সাধারণ list-based approach** (ছোট কথোপকথনের জন্য):
```python
conversation = []
conversation.append(HumanMessage(content="আমার নাম রাহুল।"))
conversation.append(model.invoke(conversation))
conversation.append(HumanMessage(content="আমার নাম কী?"))
response = model.invoke(conversation)  # আগের context থেকে "রাহুল" বলতে পারবে
```

**খ) `trim_messages`** — পুরনো মেসেজ ছেঁটে token limit-এর মধ্যে রাখা:
```python
from langchain_core.messages import trim_messages

trimmed = trim_messages(
    conversation,
    max_tokens=1000,
    strategy="last",       # শেষের মেসেজগুলো রাখো
    token_counter=model,
    include_system=True,   # SystemMessage সবসময় রাখো
)
```

**গ) `RunnableWithMessageHistory` / LangGraph checkpointer** — প্রোডাকশন অ্যাপে session-ভিত্তিক memory persist করার জন্য, যেখানে প্রতিটা user-এর আলাদা `session_id` থাকে এবং history ডাটাবেসে/মেমোরিতে সংরক্ষিত থাকে।

---

আপনি কোন দিকে কাজ করছেন — একটা **chatbot বানাচ্ছেন** (তাহলে memory management গুরুত্বপূর্ণ), নাকি **agent/tool-calling** নিয়ে কাজ করছেন (তাহলে ToolMessage), নাকি **UI/frontend** নিয়ে (তাহলে streaming)?