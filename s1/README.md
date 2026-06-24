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