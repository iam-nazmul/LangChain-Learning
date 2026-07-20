## LangChain‑এর জন্য পেশাদারদের সর্বোত্তম অনুশীলন গাইডলাইন (বাংলা)

> **নোট:** এই গাইডটি Python‑ভিত্তিক LangChain ব্যবহারকে কেন্দ্র করে তৈরি করা হয়েছে, তবে ধারণাগুলো অন্য ভাষা/ফ্রেমওয়ার্কেও প্রযোজ্য।

---

### ১. প্রকল্পের গঠন (Project Structure)

| ফোল্ডার / ফাইল | উদ্দেশ্য | উদাহরণ |
|----------------|----------|--------|
| `src/` | মূল কোড (চেইন, টুল, মডেল ইন্টারফেস) | `src/chains/`, `src/tools/`, `src/prompts/` |
| `tests/` | ইউনিট/ইন্টিগ্রেশন টেস্ট | `pytest` ব্যবহার করে |
| `configs/` | YAML/JSON‑এ পরিবেশ‑নির্দিষ্ট কনফিগ | `dev.yaml`, `prod.yaml` |
| `scripts/` | ডেটা প্রিপ্রসেস, মডেল ডিপ্লয় স্ক্রিপ্ট | `scripts/run_server.py` |
| `requirements.txt` বা `pyproject.toml` | ডিপেন্ডেন্সি ম্যানেজমেন্ট | `langchain==0.2.*` |
| `Dockerfile` | কন্টেইনারাইজেশন | `FROM python:3.11-slim` |
| `README.md` | প্রকল্পের সারসংক্ষেপ, চালানোর ধাপ | – |

**সেরা অনুশীলন:**  
- **মডুলারাইজেশন** – প্রতিটি চেইন, টুল, প্রম্পট আলাদা মডিউলে রাখুন।  
- **ইম্পোর্ট স্টাইল** – `from src.chains import SummarizeChain` এর মতো অ্যাবসোলিউট ইম্পোর্ট ব্যবহার করুন।  
- **টাইপ হিন্ট** – `from typing import List, Dict` ব্যবহার করে কোডের রিডেবিলিটি বাড়ান।

---

### ২. পরিবেশ ও সিকিউরিটি (Environment & Security)

| বিষয় | কীভাবে হ্যান্ডেল করবেন |
|------|------------------------|
| **সিক্রেট ম্যানেজমেন্ট** | `python-dotenv` বা `AWS Secrets Manager` ব্যবহার করুন। `.env` ফাইলকে **gitignore**‑এ রাখুন। |
| **API রেট‑লিমিট** | রেট‑লিমিট হ্যান্ডলিং লজিক (exponential backoff) যোগ করুন। |
| **ডেটা প্রাইভেসি** | ব্যবহারকারীর ইনপুট লগ না করা (বা হ্যাশ করা) নিশ্চিত করুন। GDPR/PDPA‑এর সাথে সামঞ্জস্য রাখুন। |
| **ডিপেন্ডেন্সি স্ক্যান** | `pip-audit` বা `safety` দিয়ে সিকিউরিটি ভলনারেবিলিটি চেক করুন। |
| **কন্টেইনার সিকিউরিটি** | `non-root` ইউজার দিয়ে Docker ইমেজ রান করুন, `--read-only` ফাইলসিস্টেম ব্যবহার করুন। |

---

### ৩. প্রম্পট ডিজাইন (Prompt Engineering)

1. **সুস্পষ্ট ও সংক্ষিপ্ত**  
   ```python
   PROMPT_TEMPLATE = """আপনি একজন পেশাদার ডেটা সায়েন্টিস্ট। 
   নিম্নলিখিত টেক্সটের সংক্ষিপ্তসার তৈরি করুন:
   {text}
   সংক্ষিপ্তসারটি ৩টি বাক্যে সীমাবদ্ধ রাখুন।"""
   ```

2. **ইনপুট ভ্যালিডেশন**  
   - টেক্সটের দৈর্ঘ্য চেক করুন (`len(text) <= model_token_limit`).  
   - অপ্রয়োজনীয় হোয়াইটস্পেস/HTML ট্যাগ সরিয়ে নিন।

3. **সিস্টেম ও ইউজার রোল**  
   - `ChatPromptTemplate`‑এ `system_message` দিয়ে মডেলকে রোল দিন।  
   - ইউজার ইনপুটকে `HumanMessage` হিসেবে পাস করুন।

4. **Few‑Shot উদাহরণ**  
   - গুরুত্বপূর্ণ টাস্কে ২‑৩টি উদাহরণ যোগ করুন।  
   - উদাহরণগুলোকে `PromptTemplate`‑এর `examples` ফিল্ডে রাখুন।

5. **ডাইনামিক ভেরিয়েবল**  
   - `PromptTemplate.from_template` ব্যবহার করে ভেরিয়েবল ইনজেক্ট করুন, সরাসরি স্ট্রিং ফরম্যাটিং নয়।

---

### ৪. চেইন (Chains) ও এজেন্ট (Agents)

| ধরণ | ব্যবহার | উদাহরণ |
|------|--------|--------|
| **SequentialChain** | একাধিক স্টেপ ধারাবাহিকভাবে চালাতে | `Extract → Summarize → Translate` |
| **RouterChain** | ইনপুটের ভিত্তিতে ভিন্ন চেইন রাউট করতে | `if "code" in query: CodeChain else: QAChain` |
| **AgentExecutor** | টুল কলের মাধ্যমে ডায়নামিক রেজোলিউশন | `SQLToolkit`, `SearchToolkit` |
| **CustomChain** | আপনার নিজস্ব লজিক (ডেটা ফেচ, পোস্ট‑প্রসেস) | `class MyChain(Chain): ...` |

**সেরা অনুশীলন:**
- **ইনপুট/আউটপুট স্পেসিফিকেশন** – `input_keys`, `output_keys` স্পষ্টভাবে ডিফাইন করুন।  
- **ক্যাশিং** – একই ইনপুটের জন্য `@lru_cache` বা `langchain.cache` ব্যবহার করুন।  
- **টুল রেজিস্ট্রি** – টুলগুলোকে `Tool` অবজেক্টে র‍্যাপ করে `AgentExecutor`‑এ পাস করুন।  
- **টাইমআউট** – দীর্ঘ‑চলমান টাস্কে `timeout` প্যারামিটার দিন।

```python
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# উদাহরণ: টেক্সট এক্সট্র্যাকশন → সারাংশ
extract_prompt = PromptTemplate.from_template(
    "দেওয়া ডকুমেন্ট থেকে মূল পয়েন্টগুলো বের করুন:\n{doc}"
)
summarize_prompt = PromptTemplate.from_template(
    "উপরের পয়েন্টগুলোকে ২টি বাক্যে সংক্ষেপ করুন।"
)

extract_chain = LLMChain(llm=OpenAI(), prompt=extract_prompt, output_key="points")
summarize_chain = LLMChain(llm=OpenAI(), prompt=summarize_prompt, output_key="summary")

pipeline = SequentialChain(
    chains=[extract_chain, summarize_chain],
    input_variables=["doc"],
    output_variables=["summary"]
)
```

---

### ৫. মেমরি (Memory) ব্যবহারে টিপস

| মেমরি টাইপ | কখন ব্যবহার করবেন |
|------------|-------------------|
| **ConversationBufferMemory** | সাধারণ চ্যাটবট, পুরো কথোপকথন সংরক্ষণ। |
| **ConversationSummaryMemory** | দীর্ঘ সেশন, সংক্ষিপ্তসার রেখে টোকেন সেভ। |
| **VectorStoreRetrieverMemory** | রিট্রিভাল‑অগমেন্টেড জেনারেশন (RAG)‑এ ডকুমেন্ট রিলেভ্যান্স বজায় রাখতে। |

**প্র্যাকটিক্যাল টিপস**
- **টোকেন সীমা**: মেমরি রিট্রিভাল করার আগে `max_token_limit` চেক করুন।  
- **ডেটা পারসিস্টেন্স**: `Redis`, `PostgreSQL` বা `FAISS`‑এ মেমরি সেভ করুন, যাতে রিস্টার্টে ডেটা হারিয়ে না যায়।  
- **প্রাইভেসি**: ব্যবহারকারীর সংবেদনশীল তথ্য মেমরিতে রাখবেন না; হ্যাশ বা এনক্রিপ্ট করে সংরক্ষণ করুন।

```python
from langchain.memory import ConversationSummaryMemory
from langchain.llms import OpenAI

memory = ConversationSummaryMemory(
    llm=OpenAI(),
    max_token_limit=1500,
    return_messages=True
)
```

---

### ৬. রিট্রিভাল‑অগমেন্টেড জেনারেশন (RAG)

1. **ডেটা ইনজেস্ট**  
   - `DocumentLoader` (CSV, PDF, Web) ব্যবহার করে ডকুমেন্ট লোড করুন।  
   - টেক্সট ক্লিনিং → সেম্যান্টিক সেগমেন্টেশন (চাঙ্ক সাইজ ৪০০‑৬০০ টোকেন)।

2. **ইন্ডেক্সিং**  
   - `FAISS`, `Chroma`, `Pinecone` ইত্যাদি ভেক্টর স্টোরে ইনডেক্স করুন।  
   - মেটাডেটা (source, timestamp) সংরক্ষণ করুন।

3. **রিট্রিভার**  
   - `Retriever`‑কে `TopK` (সাধারণত ৩‑৫) সেট করুন।  
   - রিট্রিভড ডকুমেন্টকে `PromptTemplate`‑এ ইনজেক্ট করুন।

4. **ডাউনস্ট্রিম চেইন**  
   - রিট্রিভড ডকুমেন্ট + ইউজার কোয়েরি → `LLMChain` (প্রম্পটে `Context:` যোগ করুন)।

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

loader = PyPDFLoader("policy.pdf")
docs = loader.load_and_split(text_splitter=RecursiveCharacterTextSplitter(chunk_size=500))

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=retriever,
    return_source_documents=True
)
```

---

### ৭. লগিং, মনিটরিং ও অডিট (Logging, Monitoring & Auditing)

| টুল | ব্যবহার |
|-----|----------|
| **loguru** | স্ট্রাকচার্ড লগ (JSON) |
| **Prometheus + Grafana** | রিকোয়েস্ট লেটেন্সি, টোকেন ব্যবহার, ত্রুটি রেট |
| **Sentry** | এক্সসেপশন ট্র্যাকিং |
| **OpenTelemetry** | ডিস্ট্রিবিউটেড ট্রেসিং (যদি মাইক্রোসার্ভিসে ডিপ্লয় করেন) |

**লগ ফরম্যাট উদাহরণ (JSON):**
```json
{
  "timestamp": "2026-07-12T14:23:45Z",
  "level": "INFO",
  "request_id": "a1b2c3d4",
  "user_id": "U12345",
  "prompt_tokens": 124,
  "completion_tokens": 312,
  "total_cost_usd": 0.0012,
  "status": "SUCCESS"
}
```

- **কস্ট ট্র্যাকিং** – `OpenAI`‑এর `usage` রেসপন্স থেকে টোকেন সংখ্যা বের করে ডেটাবেজে সঞ্চয় করুন।  
- **অ্যালার্ট** – টোকেন ব্যবহার নির্দিষ্ট থ্রেশহোল্ড অতিক্রম করলে Slack/Email অ্যালার্ট।

---

### ৮. টেস্টিং ও CI/CD

| টেস্টের ধরন | কীভাবে করবেন |
|------------|----------------|
| **ইউনিট টেস্ট** | `pytest` + `pytest-mock` দিয়ে LLM কলকে মক করুন (`MockOpenAI`). |
| **ইন্টিগ্রেশন টেস্ট** | ছোট‑সাইজের রিট্রিভার (FAISS‑in‑memory) দিয়ে পুরো চেইন চালান। |
| **পারফরম্যান্স টেস্ট** | `locust` বা `k6` দিয়ে রিকোয়েস্ট লেটেন্সি মাপুন। |
| **ডেটা ভ্যালিডেশন** | `pydantic` মডেল দিয়ে ইনপুট/আউটপুট স্কিমা নিশ্চিত করুন। |

**CI/CD পাইললাইন (GitHub Actions) উদাহরণ:**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-mock
      - name: Run tests
        run: pytest -v --cov=src
```

---

### ৯. ডিপ্লয়মেন্ট ও স্কেলিং

| পরিবেশ | কীভাবে ডিপ্লয় করবেন |
|--------|----------------------|
| **Docker** | `docker build -t my-langchain-app .` → `docker run -p 8000:8000` |
| **Kubernetes** | `Deployment` + `HorizontalPodAutoscaler` (CPU/Memory ভিত্তিক) |
| **Serverless (AWS Lambda)** | `aws-l
