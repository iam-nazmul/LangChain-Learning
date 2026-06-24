# LangChain শেখার সম্পূর্ণ গাইডলাইন — শূন্য থেকে প্রফেশনাল

> হালনাগাদ: ২০২৬ সালের ইকোসিস্টেম অনুযায়ী (LangChain 1.0, LangGraph 1.0, LangSmith)। এই গাইডে শুধু `langchain` নয়, পুরো আধুনিক স্ট্যাকটাই কভার করা হয়েছে, কারণ ২০২৬-এ একটা সাধারণ LLM wrapper বানানোই যথেষ্ট নয় — অ্যাপ্লিকেশনকে হতে হয় নির্ভরযোগ্য (reliable), স্টেটফুল (stateful) ও পর্যবেক্ষণযোগ্য (observable)।

---

## ০. শুরুর আগে: পুরো ছবিটা বুঝে নিন

LangChain এখন আর একটা মাত্র লাইব্রেরি নয় — এটা তিনটি স্তম্ভের একটা ইকোসিস্টেম। এই তিনটার ভূমিকা গুলিয়ে ফেললে শেখার পথ অগোছালো হয়ে যায়, তাই প্রথমেই পরিষ্কার করে নিন:

| টুল | কাজ | কখন লাগে |
|---|---|---|
| **LangChain** | বিল্ডিং ব্লক — models, prompts, tools, retrieval, এবং high-level এজেন্ট তৈরির সবচেয়ে দ্রুত উপায় | প্রায় সব প্রজেক্টে, শুরু থেকেই |
| **LangGraph** | অর্কেস্ট্রেশন রানটাইম — জটিল, লুপিং, স্টেটফুল, দীর্ঘ-চলমান এজেন্টের ওপর নিম্নস্তরের নিয়ন্ত্রণ | যখন এজেন্টকে "মনে রাখতে" হয়, branching/looping লাগে, বা সার্ভার রিস্টার্টেও কাজ চালিয়ে যেতে হয় |
| **LangSmith** | অবজার্ভেবিলিটি — tracing, evaluation, monitoring, deployment | যখন প্রোডাকশনে নিয়ে যাবেন এবং ডিবাগ/মূল্যায়ন করতে হবে |

একটা গুরুত্বপূর্ণ কথা মাথায় রাখুন: **LangChain-এর এজেন্ট গুলো LangGraph-এর ওপর তৈরি।** তাই আপনি high-level API দিয়ে শুরু করে যখন বেশি নিয়ন্ত্রণ দরকার হবে, তখন নিচে LangGraph-এ নেমে আসতে পারবেন — কোনো lock-in নেই।

### এই গাইড শেষ করলে আপনি পারবেন
- LCEL দিয়ে দক্ষ, composable AI পাইপলাইন বানাতে
- নিজের ডেটার ওপর প্রশ্নোত্তর করা RAG সিস্টেম বানাতে
- টুল ব্যবহার করতে পারে এমন স্বয়ংক্রিয় এজেন্ট বানাতে
- LangGraph দিয়ে স্টেটফুল, persistent এজেন্ট আর্কিটেকচার ডিজাইন করতে
- LangSmith দিয়ে প্রোডাকশনে ট্রেস, মূল্যায়ন ও মনিটর করতে

---

## পূর্বশর্ত (Prerequisites)

LangChain-এ ঝাঁপ দেওয়ার আগে এগুলো থাকা চাই। না থাকলে আগে এগুলোতে কিছুদিন দিন — পরে অনেক হতাশা বাঁচবে।

1. **Python (মাঝারি স্তর)** — functions, classes, decorators, list/dict comprehension, async/await-এর প্রাথমিক ধারণা, virtual environment ব্যবহার।
2. **API ও JSON** — REST API কী, request/response, environment variable দিয়ে API key ম্যানেজ করা।
3. **LLM-এর প্রাথমিক ধারণা** — token কী, prompt কী, temperature কী, context window কী। (গভীর জানা লাগবে না, ধারণা থাকলেই হবে।)
4. **Git/GitHub-এর বেসিক** — কোড ভার্সন করা ও প্রজেক্ট শেয়ার করা।

> পরামর্শ: আপনার যদি Python দুর্বল হয়, প্রথমে ২–৩ সপ্তাহ শুধু Python-এ দিন। LangChain-এর অর্ধেক সমস্যা আসলে Python-এর সমস্যা।

---

## পর্যায় ০ — পরিবেশ সেটআপ (১ দিন)

```bash
# একটি ফোল্ডার ও virtual environment বানান
mkdir langchain-learning && cd langchain-learning
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# মূল প্যাকেজগুলো ইনস্টল করুন (২০২৬ সংস্করণ)
pip install -U langchain langgraph langsmith
pip install -U langchain-openai      # অথবা langchain-anthropic, langchain-google-genai ইত্যাদি
pip install -U python-dotenv
```

`.env` ফাইলে আপনার key রাখুন (কখনো কোডে সরাসরি লিখবেন না):

```env
OPENAI_API_KEY=sk-...
# LangSmith ব্যবহার করলে (পরের দিকে লাগবে):
LANGSMITH_API_KEY=ls-...
LANGSMITH_TRACING=true
```

প্রথম "Hello World" — মডেল ঠিকমতো রেসপন্ড করছে কিনা যাচাই করুন:

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")
print(model.invoke("এক বাক্যে বলো LangChain কী?").content)
```

এটা চললে আপনি প্রস্তুত।

---

## পর্যায় ১ — বিগিনার: ফাউন্ডেশন (সপ্তাহ ১–২)

এই পর্যায়ের লক্ষ্য: LangChain-এর মূল বিল্ডিং ব্লক ও **LCEL (LangChain Expression Language)** আয়ত্ত করা। LCEL হলো সেই syntax যা দিয়ে আপনি ছোট ছোট অংশ জুড়ে (`|` পাইপ দিয়ে) একটা চেইন বানান।

### যা শিখবেন
1. **Chat Models ও Messages** — `SystemMessage`, `HumanMessage`, `AIMessage`-এর ভূমিকা।
2. **Prompt Templates** — ডায়নামিক ইনপুট সহ প্রম্পট তৈরি (`ChatPromptTemplate`)।
3. **Output Parsers** — মডেলের আউটপুটকে কাঠামোবদ্ধ করা (`StrOutputParser`, Pydantic দিয়ে structured output)।
4. **LCEL ও Runnables** — `invoke`, `batch`, `stream`; এবং `RunnableParallel`, `RunnablePassthrough`, `RunnableBranch`।

### উদাহরণ: একটি সিম্পল LCEL চেইন

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "তুমি একজন সহায়ক বাংলা শিক্ষক।"),
    ("human", "{topic} বিষয়টি একজন শিশুকে বোঝাও।"),
])
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | model | parser          # ← এটাই LCEL
print(chain.invoke({"topic": "মাধ্যাকর্ষণ"}))
```

### structured output (পেশাদারিত্বের জন্য জরুরি)

```python
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str = Field(description="সিনেমার নাম")
    rating: int = Field(description="১০-এর মধ্যে রেটিং")
    summary: str

structured_model = model.with_structured_output(MovieReview)
result = structured_model.invoke("Inception সিনেমাটির একটি রিভিউ দাও।")
print(result.rating, result.summary)
```

### 🎯 প্র্যাকটিস প্রজেক্ট
- একটি **CLI চ্যাটবট** যা ইউজারের প্রশ্নের উত্তর দেয়।
- একটি **টেক্সট সামারাইজার** — লম্বা লেখা ইনপুট নিয়ে ৩ লাইনে সারসংক্ষেপ দেয়।
- structured output দিয়ে একটি **রিভিউ অ্যানালাইজার** (rating + sentiment বের করে)।

---

## পর্যায় ২ — ইন্টারমিডিয়েট: RAG ও মেমরি (সপ্তাহ ৩–৪)

এখানেই LangChain-এর আসল শক্তি দেখা যায়। **RAG (Retrieval-Augmented Generation)** মানে মডেলকে শুধু তার নিজের জ্ঞানের ওপর ছেড়ে না দিয়ে আপনার নিজস্ব ডেটা (PDF, ওয়েবসাইট, ডেটাবেস) থেকে প্রাসঙ্গিক তথ্য খুঁজে এনে উত্তর তৈরি করানো।

> ২০২৬-এর বাস্তবতা: কার্যকর RAG আর শুধু "একটা vector search" নয় — এটা একটা কাঠামোবদ্ধ পাইপলাইন যার মান (quality) মাপা ও রক্ষণাবেক্ষণ করা যায়।

### RAG পাইপলাইনের ধাপগুলো
1. **Document Loaders** — সোর্স থেকে ডেটা আনা (`PyPDFLoader`, `WebBaseLoader` ইত্যাদি)।
2. **Text Splitters** — বড় ডকুমেন্টকে ছোট chunk-এ ভাঙা (`RecursiveCharacterTextSplitter`)।
3. **Embeddings** — টেক্সটকে সংখ্যায় (vector) রূপান্তর।
4. **Vector Stores** — vector সংরক্ষণ ও খোঁজা (`Chroma`, `FAISS`, `Qdrant`, `Pinecone`)।
5. **Retrievers** — প্রশ্নের সাথে মিলিয়ে প্রাসঙ্গিক chunk খুঁজে আনা।

### একটি ন্যূনতম RAG পাইপলাইন

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. লোড ও স্প্লিট
docs = WebBaseLoader("https://example.com/article").load()
splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

# 2. embed ও store
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 3. RAG চেইন
prompt = ChatPromptTemplate.from_template(
    "শুধু নিচের context ব্যবহার করে উত্তর দাও:\n\n{context}\n\nপ্রশ্ন: {question}"
)
model = ChatOpenAI(model="gpt-4o-mini")

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | model | StrOutputParser()
)
print(rag_chain.invoke("আর্টিকেলের মূল বক্তব্য কী?"))
```

### মেমরি (Conversation Memory)
চ্যাটবটকে আগের কথোপকথন মনে রাখাতে হলে message history সংরক্ষণ করতে হয়। ২০২৬-এ এর আধুনিক ও পছন্দনীয় উপায় হলো **LangGraph-এর persistence/checkpointer** (পরের পর্যায়ে আসছে), পুরোনো `ConversationBufferMemory`-এর বদলে।

### 🎯 প্র্যাকটিস প্রজেক্ট
- **"Chat with your PDF"** — একটি PDF আপলোড করে তার ওপর প্রশ্নোত্তর।
- একটি **ডকুমেন্টেশন অ্যাসিস্ট্যান্ট** যা কোনো লাইব্রেরির ডক পড়ে প্রশ্নের উত্তর দেয়।
- বিভিন্ন chunk_size ও retriever সেটিং বদলে আউটপুটের মান তুলনা করুন।

---

## পর্যায় ৩ — এজেন্ট: টুল ব্যবহার করা AI (সপ্তাহ ৫–৬)

চেইন একরৈখিক (linear) — শুরু থেকে শেষ পর্যন্ত একই পথ। **এজেন্ট** ভিন্ন: এটা নিজে "চিন্তা" করে সিদ্ধান্ত নেয় কোন টুল কখন ব্যবহার করবে, ফলাফল দেখে আবার চিন্তা করে — এই লুপ চলতে থাকে কাজ শেষ না হওয়া পর্যন্ত।

### যা শিখবেন
1. **Tools** — মডেলকে যেসব ফাংশন/ক্ষমতা দেওয়া হয় (ওয়েব সার্চ, ক্যালকুলেটর, API কল, নিজের লেখা Python ফাংশন)।
2. **`create_agent`** — high-level API দিয়ে দ্রুত এজেন্ট তৈরি (এটি LangGraph-এর ওপর তৈরি)।
3. **Agent loop** — reason → act (tool call) → observe → repeat।
4. **Middleware** — ১.০-এর নতুন ধারণা; এজেন্টের আচরণ কাস্টমাইজ করা, guardrails যোগ করা, এরর সামলানো, PII সুরক্ষা ইত্যাদি।
5. **Structured output from agents** — Pydantic schema দিয়ে নির্ভরযোগ্য কাঠামোবদ্ধ উত্তর।

### একটি সিম্পল টুল-ব্যবহারকারী এজেন্ট

```python
from langchain.agents import create_agent
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """দুটি সংখ্যা যোগ করে।"""
    return a + b

@tool
def get_weather(city: str) -> str:
    """একটি শহরের আবহাওয়া জানায়।"""
    return f"{city}-তে এখন ২৮° সেলসিয়াস, রোদেলা।"

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[add, get_weather],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "ঢাকার আবহাওয়া কেমন? আর ৪৫ + ৫৫ কত?"}]}
)
print(result["messages"][-1].content)
```

> নোট: পুরোনো টিউটোরিয়ালে দেখা `langgraph.prebuilt` মডিউলটি এখন deprecated; এর কার্যকারিতা `langchain.agents`-এ সরিয়ে আনা হয়েছে। তাই নতুন কোড লিখুন `langchain.agents` দিয়ে।

### 🎯 প্র্যাকটিস প্রজেক্ট
- একটি **রিসার্চ এজেন্ট** যা ওয়েব সার্চ টুল ব্যবহার করে কোনো প্রশ্নের সাম্প্রতিক উত্তর দেয়।
- একটি **ক্যালকুলেটর + ইউনিট কনভার্টার এজেন্ট**।
- একটি এজেন্ট যা আপনার নিজের একটা API (যেমন মুভি ডেটাবেস) কল করে।

---

## পর্যায় ৪ — LangGraph: স্টেটফুল ও নির্ভরযোগ্য এজেন্ট (সপ্তাহ ৭–৯)

এখান থেকেই আপনি "হবি প্রজেক্ট" পেরিয়ে "প্রোডাকশন-গ্রেড"-এর দিকে এগোন। LangGraph একটি **গ্রাফ-ভিত্তিক execution model** দেয়, যেখানে আপনার অ্যাপ্লিকেশন রৈখিক চেইন না হয়ে **state, nodes ও edges** দিয়ে গঠিত একটা স্টেট মেশিন।

### কেন LangGraph লাগে
- **Durable state** — সার্ভার রিস্টার্ট বা মাঝপথে interruption হলেও এজেন্ট ঠিক যেখানে ছিল সেখান থেকে আবার শুরু করে, context না হারিয়ে।
- **Built-in persistence (Checkpointers)** — গ্রাফের state সেভ ও resume করা; বহুদিনের approval প্রসেস বা ব্যাকগ্রাউন্ড জব সম্ভব হয়।
- **Human-in-the-loop** — উচ্চ-ঝুঁকির সিদ্ধান্তে এজেন্টকে থামিয়ে মানুষের রিভিউ/অনুমোদন নেওয়া।
- **Branching ও looping** — জটিল কন্ট্রোল ফ্লো, multi-agent আর্কিটেকচার।

### মূল ধারণাগুলো (এই ক্রমেই শিখুন)
1. **State** — গ্রাফজুড়ে যে ডেটা প্রবাহিত হয় (`TypedDict`, Pydantic, বা dict)।
2. **Nodes** — কাজের একেকটি ধাপ (একটি Python ফাংশন যা state নেয় ও আপডেট দেয়)।
3. **Edges** — কোন node-এর পর কোনটা; এবং **conditional edges** দিয়ে শর্তসাপেক্ষ পথ।
4. **Reducers** — একই state ভ্যারিয়েবলে একাধিক আপডেট কীভাবে মিলবে তার নিয়ম।
5. **Checkpointers** — persistence; `thread_id` দিয়ে আলাদা আলাদা কথোপকথন ট্র্যাক করা।
6. **`interrupt`** — human-in-the-loop-এর জন্য কার্যকর থামা।

### State, persistence ও মেমরি-সহ একটি ছোট গ্রাফ

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

class State(TypedDict):
    messages: Annotated[list, add_messages]   # add_messages = reducer

model = ChatOpenAI(model="gpt-4o-mini")

def chatbot(state: State):
    return {"messages": [model.invoke(state["messages"])]}

graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# checkpointer দিয়ে persistence — এটাই আধুনিক "মেমরি"
app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "user-1"}}
app.invoke({"messages": [{"role": "user", "content": "আমার নাম রিয়া।"}]}, config)
out = app.invoke({"messages": [{"role": "user", "content": "আমার নাম কী?"}]}, config)
print(out["messages"][-1].content)   # সে "রিয়া" মনে রাখবে
```

### 🎯 প্র্যাকটিস প্রজেক্ট
- পর্যায় ২-এর RAG চ্যাটবটকে LangGraph + checkpointer দিয়ে **মেমরি-সহ** বানান।
- একটি **multi-step এজেন্ট** যেখানে একটি node সিদ্ধান্ত নেয় (router), তারপর ভিন্ন node-এ যায়।
- একটি **human-in-the-loop** ফ্লো — এজেন্ট কোনো "ঝুঁকিপূর্ণ" কাজ (যেমন ইমেইল পাঠানো) করার আগে থামে ও অনুমোদন চায়।
- (অ্যাডভান্সড) একটি **multi-agent** সিস্টেম: একজন "রিসার্চার" + একজন "রাইটার" মিলে কাজ করে।

---

## পর্যায় ৫ — প্রোডাকশন: LangSmith দিয়ে অবজার্ভেবিলিটি ও মূল্যায়ন (সপ্তাহ ১০–১১)

এজেন্ট ডিবাগ করা কঠিন — লম্বা context, branching লজিক, অনেক টুল মিলে বোঝা মুশকিল কোথায় ভুল হলো। **LangSmith** প্রতিটি রানকে ধাপে ধাপে একটা কাঠামোবদ্ধ timeline-এ ভেঙে দেখায় — কী ঘটল, কোন ক্রমে, কেন।

### যা শিখবেন
1. **Tracing** — শুধু environment variable সেট করলেই (পর্যায় ০-এর `.env`) প্রতিটি রান স্বয়ংক্রিয়ভাবে LangSmith-এ ট্রেস হয়। প্রতিটি ধাপের ইনপুট/আউটপুট, latency, খরচ দেখা যায়।
2. **Datasets ও Evaluation** — একটা টেস্ট ডেটাসেট বানিয়ে এজেন্টের আউটপুটের মান (accuracy, relevance) মাপা।
3. **Side-by-side comparison** — প্রম্পট/মডেল/retriever বদলালে regression হলো কিনা পাশাপাশি তুলনা করে ধরা।
4. **Multi-turn evals** — শুধু একক উত্তর নয়, পুরো কথোপকথনের সফলতা মূল্যায়ন।
5. **Monitoring** — প্রোডাকশনে latency, খরচ, এরর রেট ট্র্যাক করা।

> LangSmith framework-agnostic — চাইলে LangChain ছাড়া অন্য স্ট্যাকেও ব্যবহার করা যায়। এর সাথে আছে LangSmith Engine (ব্যর্থতা ক্লাস্টার করে root cause ও ফিক্স প্রস্তাব করে) ও Insights Agent (বাস্তব ব্যবহারের ট্রেস থেকে প্যাটার্ন বের করে) — এগুলো পরে এক্সপ্লোর করবেন।

### সবচেয়ে ছোট ইভ্যালুয়েশনের ধারণা

```python
from langsmith import Client
from langsmith.evaluation import evaluate

client = Client()

# একটি ছোট ডেটাসেট: প্রশ্ন → প্রত্যাশিত উত্তর
# (LangSmith UI বা SDK দিয়ে dataset বানিয়ে নিন)

def my_app(inputs: dict) -> dict:
    # আপনার চেইন/এজেন্ট এখানে কল করুন
    return {"answer": rag_chain.invoke(inputs["question"])}

# একটি সিম্পল correctness evaluator লিখে evaluate() চালান
# evaluate(my_app, data="my-dataset", evaluators=[...])
```

### 🎯 প্র্যাকটিস প্রজেক্ট
- আপনার RAG চ্যাটবটে tracing চালু করে ১০টা প্রশ্নের ট্রেস বিশ্লেষণ করুন — কোথায় সময়/খরচ বেশি লাগছে দেখুন।
- ২০টি প্রশ্ন-উত্তরের একটি ডেটাসেট বানিয়ে দুটি ভিন্ন প্রম্পট তুলনা করুন।

---

## পর্যায় ৬ — প্রফেশনাল: ডেপ্লয়মেন্ট ও আর্কিটেকচার (সপ্তাহ ১২+)

এই পর্যায়ে আপনি একজন AI ইঞ্জিনিয়ার হিসেবে কাজ করার মতো দক্ষতা গড়েন।

### ফোকাস করুন
1. **Deployment** — এজেন্টকে API হিসেবে সার্ভ করা (FastAPI দিয়ে), অথবা LangGraph-এর ডেপ্লয়মেন্ট প্ল্যাটফর্ম ব্যবহার করা (long-running, stateful workflow-এর জন্য বিশেষভাবে তৈরি)।
2. **Safety ও Guardrails** — **tool scoping** (এজেন্ট শুধু তার ভূমিকার প্রাসঙ্গিক টুলই ব্যবহার করতে পারবে), middleware দিয়ে PII সনাক্তকরণ ও sensitive content ব্লক করা।
3. **Cost ও latency optimization** — caching, ছোট মডেল কোথায় চলে, streaming দিয়ে UX উন্নত করা।
4. **Streaming** — token-by-token আউটপুট স্ট্রিম করে এজেন্টের চিন্তা ও কাজ রিয়েল-টাইমে দেখানো।
5. **Evaluation-driven development** — প্রতিটি বদলের আগে eval চালিয়ে regression ঠেকানো।
6. **JavaScript/TypeScript** — পুরো স্ট্যাকটাই JS/TS-এও আছে (`@langchain/langgraph`); ফুল-স্ট্যাক ওয়েব অ্যাপে কাজে লাগবে।

### 🎯 ক্যাপস্টোন প্রজেক্ট আইডিয়া (একটা বেছে নিন, পূর্ণাঙ্গভাবে বানান)
- **এন্টারপ্রাইজ ডকুমেন্ট অ্যাসিস্ট্যান্ট** — অনেকগুলো PDF/ওয়েবসোর্সের ওপর RAG + মেমরি + LangSmith eval + একটা সিম্পল UI।
- **মাল্টি-এজেন্ট রিসার্চ সিস্টেম** — রিসার্চার, ফ্যাক্ট-চেকার ও রাইটার এজেন্ট মিলে একটা রিপোর্ট তৈরি করে।
- **কাস্টমার সাপোর্ট এজেন্ট** — টুল কলিং (অর্ডার লুকআপ API), human-in-the-loop (রিফান্ড অনুমোদন), guardrails ও full tracing সহ।
- **কোড-এক্সিকিউশন এজেন্ট** — LLM-এর reasoning আর Python execution আলাদা রেখে ডেটা ট্রান্সফর্ম করা।

একটা পূর্ণাঙ্গ ক্যাপস্টোন GitHub-এ ভালো README, eval রেজাল্ট ও ডেমো সহ রাখুন — এটাই আপনার পোর্টফোলিওর মূল।

---

## প্রস্তাবিত সময়সূচি (একনজরে)

| সপ্তাহ | পর্যায় | মাইলস্টোন |
|---|---|---|
| ০ (প্রি) | Python ঝালাই | comfortable Python + virtualenv |
| ১–২ | ফাউন্ডেশন | LCEL চেইন, prompts, structured output |
| ৩–৪ | RAG ও মেমরি | "Chat with PDF" কাজ করছে |
| ৫–৬ | এজেন্ট | টুল-ব্যবহারকারী এজেন্ট |
| ৭–৯ | LangGraph | স্টেটফুল, persistent, human-in-the-loop এজেন্ট |
| ১০–১১ | LangSmith | tracing + একটি eval ডেটাসেট |
| ১২+ | প্রোডাকশন | ক্যাপস্টোন ডেপ্লয় করা |

> এটা একটা গাইডলাইন, কঠোর নিয়ম নয়। ধীরে গেলে দ্বিগুণ সময় নিন — গুরুত্বপূর্ণ হলো প্রতিটি পর্যায়ে অন্তত একটা প্রজেক্ট নিজে বানানো, শুধু পড়ে যাওয়া নয়।

---

## শেখার সেরা নীতিগুলো

1. **পড়ার চেয়ে বানান বেশি।** প্রতিটি ধারণা কোড লিখে যাচাই করুন। টিউটোরিয়াল কপি করার পর অন্তত একটা জিনিস বদলে দেখুন কী হয়।
2. **অফিশিয়াল ডকই প্রধান উৎস।** এই ইকোসিস্টেম দ্রুত বদলায়; ব্লগ/ইউটিউব পুরোনো হয়ে যায়। সন্দেহ হলে `docs.langchain.com` দেখুন।
3. **ভার্সন খেয়াল রাখুন।** ১.০ আসার পর অনেক পুরোনো টিউটোরিয়াল (যেমন `LLMChain`, `initialize_agent`, পুরোনো memory ক্লাস) আর প্রাসঙ্গিক নয়। নতুন প্যাটার্ন (`LCEL`, `create_agent`, LangGraph checkpointer) ব্যবহার করুন।
4. **প্রথম দিন থেকেই খরচ ট্র্যাক করুন।** ছোট/সস্তা মডেল (যেমন `gpt-4o-mini`) দিয়ে শিখুন; API বিল বাঁচবে।
5. **এরর পড়তে শিখুন।** LangChain-এর অর্ধেক সমস্যা আসলে Python বা API key/ভার্সন সমস্যা — পুরো traceback পড়ুন।

---

## নির্ভরযোগ্য রিসোর্স

- **অফিশিয়াল ডকুমেন্টেশন** — `https://docs.langchain.com` (সবচেয়ে গুরুত্বপূর্ণ, সবসময় হালনাগাদ)
- **LangChain Academy** — LangGraph-এর ফ্রি অফিশিয়াল কোর্স (state, memory, human-in-the-loop)
- **LangChain Forum** — প্রশ্ন করা ও রোডম্যাপ আলোচনার জায়গা: `https://forum.langchain.com`
- **LangChain Changelog** — নতুন ফিচার জানতে: `https://changelog.langchain.com`
- **GitHub রিপো** — সোর্স কোড ও উদাহরণ পড়া সবচেয়ে ভালো শেখার উপায়।

---

### শেষ কথা
LangChain শেখার আসল চাবিকাঠি হলো ক্রম মেনে এগোনো: আগে চেইন বুঝুন, তারপর RAG, তারপর এজেন্ট, তারপর LangGraph দিয়ে নিয়ন্ত্রণ, এবং সবশেষে LangSmith দিয়ে মাপা ও প্রোডাকশন। মাঝপথ এড়িয়ে সরাসরি "মাল্টি-এজেন্ট সিস্টেম" বানাতে গেলে হোঁচট খাবেন। প্রতিটি পর্যায়ে একটা করে প্রজেক্ট শেষ করুন — তিন মাস পর আপনার হাতে একটা শক্ত পোর্টফোলিও থাকবে।

শুভকামনা! 🚀
