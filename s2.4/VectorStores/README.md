# Chroma — শুরু করার জন্য সহজ গাইড (বাংলায়)

## Chroma কী?

**Chroma** হলো একটি **ওপেন-সোর্স, লোকাল ভেক্টর ডেটাবেস** — মানে আপনার নিজের কম্পিউটারেই এটি চালানো যায়, আলাদা কোনো সার্ভার বা ক্লাউড অ্যাকাউন্ট লাগে না। এজন্য এটি শেখার জন্য এবং ছোট প্রজেক্টের জন্য সবচেয়ে জনপ্রিয় পছন্দ।

## কেন Chroma দিয়ে শুরু করা ভালো?

- ইনস্টল করা সহজ (`pip install chromadb`)
- API সার্ভার/অ্যাকাউন্ট লাগে না — লোকালি চলে
- সরাসরি ফাইলে ডেটা সেভ (persist) করতে পারে
- মেটাডেটা ফিল্টারিং সাপোর্ট করে
- LangChain/LlamaIndex-এর সাথে সহজেই ইন্টিগ্রেট হয়

## ইনস্টলেশন

```bash
pip install chromadb
```

## বেসিক উদাহরণ (ধাপে ধাপে)

```python
import chromadb

# ১. Client তৈরি করা (লোকাল ফোল্ডারে ডেটা সেভ হবে)
client = chromadb.PersistentClient(path="./my_chroma_db")

# ২. একটি Collection তৈরি করা (এটা অনেকটা SQL-এর "table"-এর মতো)
collection = client.get_or_create_collection(name="my_docs")

# ৩. ডেটা/ডকুমেন্ট যোগ করা
collection.add(
    documents=[
        "বাংলাদেশের রাজধানী ঢাকা",
        "পিথন একটি জনপ্রিয় প্রোগ্রামিং ভাষা",
        "ভেক্টর ডেটাবেস সেমান্টিক সার্চের জন্য ব্যবহৃত হয়"
    ],
    ids=["doc1", "doc2", "doc3"]  # প্রতিটি ডকুমেন্টের জন্য ইউনিক আইডি
)

# ৪. সার্চ করা (Query)
results = collection.query(
    query_texts=["বাংলাদেশ সম্পর্কে কিছু বলো"],
    n_results=2  # সবচেয়ে কাছের ২টি ফলাফল
)

print(results)
```

### এখানে কী ঘটলো?

- আপনাকে **নিজে embedding তৈরি করতে হয়নি** — Chroma ডিফল্টভাবে নিজেই একটি ছোট embedding model ব্যবহার করে টেক্সটকে ভেক্টরে রূপান্তর করে ফেলেছে
- `query_texts` দিয়ে যা জিজ্ঞেস করেছেন, সেটার সাথে **অর্থগতভাবে সবচেয়ে কাছের** ডকুমেন্টগুলো ফেরত এসেছে (এক্স্যাক্ট শব্দ মিল না থাকলেও)

## মেটাডেটা সহ উদাহরণ (বাস্তব ব্যবহার)

```python
collection.add(
    documents=["ঢাকা শহরের ট্রাফিক সমস্যা নিয়ে একটি প্রতিবেদন"],
    metadatas=[{"category": "news", "year": 2025}],
    ids=["doc4"]
)

# মেটাডেটা দিয়ে ফিল্টার করে সার্চ
results = collection.query(
    query_texts=["ঢাকার সমস্যা"],
    n_results=1,
    where={"category": "news"}  # শুধু "news" ক্যাটাগরির মধ্যে খুঁজবে
)
```

## নিজের Embedding Model ব্যবহার করতে চাইলে (যেমন OpenAI)

```python
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_API_KEY",
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="my_docs_openai",
    embedding_function=openai_ef
)
```

## গুরুত্বপূর্ণ পয়েন্ট (মনে রাখার জন্য)

| বিষয় | ব্যাখ্যা |
|---|---|
| `PersistentClient` | ডেটা ডিস্কে সেভ থাকে, প্রোগ্রাম বন্ধ করলেও হারায় না |
| `Client()` (in-memory) | শুধু RAM-এ থাকে, প্রোগ্রাম বন্ধ হলে ডেটা মুছে যায় — টেস্টিং-এর জন্য ভালো |
| `collection.add()` | নতুন ডেটা/ডকুমেন্ট যোগ করার জন্য |
| `collection.query()` | সিমিলারিটি সার্চের জন্য |
| `ids` | প্রতিটি ডকুমেন্টের ইউনিক আইডি — বাধ্যতামূলক |

## পরবর্তী ধাপ

শেখার একটি স্বাভাবিক পথ হতে পারে:
1. ছোট ছোট টেক্সট দিয়ে বেসিক add/query প্র্যাকটিস করা (উপরের মতো)
2. একটি PDF/ডকুমেন্টকে chunk করে Chroma-তে লোড করা (RAG-এর প্রথম ধাপ)
3. LangChain-এর সাথে Chroma ইন্টিগ্রেট করে একটি ছোট Q&A সিস্টেম বানানো



---



বুঝেছি, চলুন একটি সম্পূর্ণ **Mini RAG প্রজেক্ট** বানাই — PDF পড়ে প্রশ্নের উত্তর দেবে এমন একটি সিস্টেম। ধাপে ধাপে বাংলায় ব্যাখ্যাসহ কোড দিচ্ছি।

## প্রজেক্টের কাঠামো (Flow)

```
PDF ফাইল → টেক্সট বের করা → ছোট ছোট Chunk-এ ভাগ করা 
→ Embedding তৈরি → Chroma-তে সংরক্ষণ 
→ প্রশ্ন করলে সবচেয়ে কাছের Chunk খোঁজা 
→ LLM (যেমন OpenAI) দিয়ে সেই তথ্যের ভিত্তিতে উত্তর তৈরি
```

## প্রয়োজনীয় লাইব্রেরি ইনস্টল

```bash
pip install chromadb langchain langchain-community langchain-openai pypdf openai
```

## সম্পূর্ণ কোড

```python
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# ===== ০. API Key সেট করা =====
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY_HERE"

# ===== ১. PDF পড়া =====
pdf_path = "example.pdf"  # আপনার PDF ফাইলের পথ
loader = PyPDFLoader(pdf_path)
documents = loader.load()
print(f"মোট পেজ পাওয়া গেছে: {len(documents)}")

# ===== ২. টেক্সটকে ছোট Chunk-এ ভাগ করা =====
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # প্রতিটি অংশ কত অক্ষরের হবে
    chunk_overlap=150     # অংশগুলোর মধ্যে overlap (context না হারানোর জন্য)
)
chunks = text_splitter.split_documents(documents)
print(f"মোট chunk তৈরি হয়েছে: {len(chunks)}")

# ===== ৩. Embedding তৈরি করে Chroma-তে সংরক্ষণ =====
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_pdf_db"  # ডিস্কে সেভ হবে
)

# ===== ৪. Retriever তৈরি (সার্চের জন্য) =====
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}  # সবচেয়ে কাছের ৩টি chunk আনবে
)

# ===== ৫. LLM + RAG চেইন তৈরি =====
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",       # সব context একসাথে prompt-এ পাঠাবে
    retriever=retriever,
    return_source_documents=True
)

# ===== ৬. প্রশ্ন করা =====
def ask_question(query):
    result = qa_chain.invoke({"query": query})
    print("\n📌 উত্তর:", result["result"])
    print("\n📄 সোর্স (কোন অংশ থেকে উত্তর এসেছে):")
    for doc in result["source_documents"]:
        print("-", doc.page_content[:150], "...")

# উদাহরণ
ask_question("এই ডকুমেন্টের মূল বিষয়বস্তু কী?")
```

## কোন অংশ কী কাজ করছে (সংক্ষেপে)

| ধাপ | কাজ |
|---|---|
| `PyPDFLoader` | PDF থেকে টেক্সট বের করে, পেজ অনুযায়ী ভাগ করে |
| `RecursiveCharacterTextSplitter` | বড় টেক্সটকে ছোট chunk-এ ভাগ করে (LLM-এর context limit মাথায় রেখে) |
| `OpenAIEmbeddings` | প্রতিটি chunk-কে ভেক্টরে রূপান্তর করে |
| `Chroma.from_documents` | ভেক্টরগুলো সংরক্ষণ করে এবং persist করে |
| `retriever` | প্রশ্নের সাথে মিলযুক্ত chunk খুঁজে বের করে |
| `RetrievalQA` | পাওয়া chunk-গুলো LLM-কে দিয়ে উত্তর তৈরি করায় |

## পরে আবার চালাতে চাইলে (re-embedding ছাড়াই)

একবার সেভ করার পর, প্রতিবার নতুন করে PDF process করতে হবে না — শুধু আগের DB লোড করলেই হবে:

```python
vectorstore = Chroma(
    persist_directory="./chroma_pdf_db",
    embedding_function=embeddings
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

## গুরুত্বপূর্ণ নোট

- **OpenAI API key** লাগবে (অথবা চাইলে ফ্রি/লোকাল বিকল্প যেমন **HuggingFace embeddings + Ollama** দিয়েও করা যায় — খরচ ছাড়াই)
- `chunk_size` ও `k` (কয়টা chunk আনবে) পরিবর্তন করে ফলাফলের গুণগত মান ঠিক করা যায়

আপনি কি **OpenAI (paid)** দিয়ে করতে চান, নাকি সম্পূর্ণ **ফ্রি/লোকাল** (Ollama + HuggingFace embedding) ভার্সন দেখতে চান?



---

# সম্পূর্ণ ফ্রি/লোকাল RAG প্রজেক্ট (Ollama + HuggingFace Embedding)

এই ভার্সনে **কোনো API key বা খরচ লাগবে না** — সবকিছু আপনার নিজের কম্পিউটারে চলবে।

## যা যা লাগবে

1. **Ollama** — লোকালি LLM চালানোর টুল
2. **HuggingFace Embeddings** — ফ্রি, লোকাল embedding model
3. **Chroma** — ভেক্টর স্টোর

## ধাপ ১: Ollama ইনস্টল করা

প্রথমে Ollama ইনস্টল করুন: https://ollama.com/download

তারপর টার্মিনালে একটি মডেল ডাউনলোড করুন (যেমন `llama3` বা হালকা মডেল `phi3`):

```bash
ollama pull llama3
```

Ollama ব্যাকগ্রাউন্ডে সার্ভার হিসেবে চলতে থাকবে (`http://localhost:11434`)।

## ধাপ ২: প্রয়োজনীয় Python লাইব্রেরি ইনস্টল

```bash
pip install chromadb langchain langchain-community pypdf sentence-transformers
```

## ধাপ ৩: সম্পূর্ণ কোড

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# ===== ১. PDF পড়া =====
pdf_path = "example.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()
print(f"মোট পেজ পাওয়া গেছে: {len(documents)}")

# ===== ২. টেক্সটকে Chunk-এ ভাগ করা =====
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150
)
chunks = text_splitter.split_documents(documents)
print(f"মোট chunk তৈরি হয়েছে: {len(chunks)}")

# ===== ৩. ফ্রি HuggingFace Embedding মডেল =====
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # ছোট, দ্রুত, ফ্রি
)

# ===== ৪. Chroma-তে সংরক্ষণ =====
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_pdf_db_local"
)

# ===== ৫. Retriever তৈরি =====
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ===== ৬. লোকাল LLM (Ollama) =====
llm = Ollama(model="llama3")  # আগে ollama pull llama3 করা থাকতে হবে

# ===== ৭. RAG চেইন তৈরি =====
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# ===== ৮. প্রশ্ন করা =====
def ask_question(query):
    result = qa_chain.invoke({"query": query})
    print("\n📌 উত্তর:", result["result"])
    print("\n📄 সোর্স:")
    for doc in result["source_documents"]:
        print("-", doc.page_content[:150], "...")

ask_question("এই ডকুমেন্টের মূল বিষয়বস্তু কী?")
```

## OpenAI ভার্সনের সাথে পার্থক্য (কী বদলেছে)

| বিষয় | OpenAI ভার্সন | ফ্রি/লোকাল ভার্সন |
|---|---|---|
| Embedding | `OpenAIEmbeddings` (paid API) | `HuggingFaceEmbeddings` (ফ্রি, লোকাল) |
| LLM | `ChatOpenAI` (paid API) | `Ollama` (লোকাল, ফ্রি) |
| ইন্টারনেট দরকার? | হ্যাঁ (প্রতি রিকোয়েস্টে) | না (একবার মডেল ডাউনলোডের পর) |
| খরচ | টোকেন অনুযায়ী | সম্পূর্ণ ফ্রি |
| গতি | দ্রুত (ক্লাউড সার্ভার) | আপনার কম্পিউটারের হার্ডওয়্যারের উপর নির্ভরশীল |

## গুরুত্বপূর্ণ বিষয়

- **RAM প্রয়োজন:** `llama3` মডেলের জন্য কমপক্ষে ৮GB RAM ভালো, কম হলে হালকা মডেল ব্যবহার করুন:
  ```bash
  ollama pull phi3
  ```
  আর কোডে `Ollama(model="phi3")` করে দিন।

- **প্রথমবার চালাতে সময় লাগবে** — HuggingFace embedding model ও Ollama মডেল প্রথমবার ডাউনলোড হবে।

- **GPU না থাকলেও চলবে**, তবে CPU-তে একটু ধীরগতিতে উত্তর আসবে।

## পরবর্তী ধাপ (ঐচ্ছিক)

চাইলে আমি এটাকে একটি **সহজ Web UI (Streamlit)** দিয়ে সাজিয়ে দিতে পারি, যেখানে আপনি PDF আপলোড করে সরাসরি প্রশ্ন লিখতে পারবেন — কোনো টার্মিনাল/কোড ছাড়াই ব্যবহার করা যাবে। এটা দেখতে চান?


---

# Streamlit Web UI দিয়ে সম্পূর্ণ RAG অ্যাপ

চলুন এবার আগের কোডটাকে একটি সুন্দর **Web UI**-তে রূপান্তর করি — যেখানে PDF আপলোড করা যাবে এবং সরাসরি প্রশ্ন লিখে উত্তর পাওয়া যাবে।

## ইনস্টলেশন

```bash
pip install streamlit chromadb langchain langchain-community pypdf sentence-transformers
```

## সম্পূর্ণ কোড (`app.py`)

```python
import streamlit as st
import tempfile
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# ===== পেজ কনফিগারেশন =====
st.set_page_config(page_title="PDF Q&A (RAG)", page_icon="📄", layout="centered")
st.title("📄 PDF প্রশ্ন-উত্তর সিস্টেম (ফ্রি ও লোকাল)")
st.caption("Ollama + HuggingFace + Chroma ব্যবহার করে তৈরি")

# ===== Session State (একবার লোড হলে বারবার লোড না করার জন্য) =====
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

# ===== সাইডবার: মডেল সিলেকশন =====
with st.sidebar:
    st.header("⚙️ সেটিংস")
    model_name = st.selectbox(
        "Ollama মডেল নির্বাচন করুন",
        ["llama3", "phi3", "mistral"],
        help="আগে থেকে 'ollama pull <model>' দিয়ে ডাউনলোড করা থাকতে হবে"
    )
    chunk_size = st.slider("Chunk Size", 500, 2000, 1000, step=100)
    k_value = st.slider("কয়টা সোর্স খুঁজবে (k)", 1, 5, 3)

# ===== ফাইল আপলোড =====
uploaded_file = st.file_uploader("📤 একটি PDF ফাইল আপলোড করুন", type="pdf")

# ===== PDF প্রসেস করার ফাংশন =====
def process_pdf(file, chunk_size, k_value, model_name):
    with st.spinner("PDF প্রসেস হচ্ছে... একটু সময় লাগবে ⏳"):
        # টেম্প ফাইলে সেভ করা
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # ১. PDF লোড
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # ২. Chunk ভাগ করা
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=150
        )
        chunks = splitter.split_documents(documents)

        # ৩. Embedding
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # ৪. Chroma vectorstore (in-memory, প্রতিটি নতুন ফাইলের জন্য আলাদা)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k_value})

        # ৫. LLM
        llm = Ollama(model=model_name)

        # ৬. QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )

        os.unlink(tmp_path)  # টেম্প ফাইল মুছে ফেলা
        return qa_chain, len(chunks)

# ===== ফাইল প্রসেসিং লজিক =====
if uploaded_file is not None:
    if st.session_state.processed_file != uploaded_file.name:
        qa_chain, num_chunks = process_pdf(uploaded_file, chunk_size, k_value, model_name)
        st.session_state.qa_chain = qa_chain
        st.session_state.processed_file = uploaded_file.name
        st.success(f"✅ '{uploaded_file.name}' প্রসেস সম্পন্ন! ({num_chunks} টি chunk তৈরি হয়েছে)")
    else:
        st.info(f"📌 '{uploaded_file.name}' ইতিমধ্যে লোড করা আছে")

# ===== প্রশ্ন করার সেকশন =====
if st.session_state.qa_chain is not None:
    st.divider()
    query = st.text_input("❓ আপনার প্রশ্ন লিখুন:")

    if st.button("উত্তর খুঁজুন 🔍") and query:
        with st.spinner("উত্তর তৈরি হচ্ছে..."):
            result = st.session_state.qa_chain.invoke({"query": query})

        st.markdown("### 📌 উত্তর")
        st.write(result["result"])

        with st.expander("📄 কোন অংশ থেকে উত্তর এসেছে (সোর্স) দেখুন"):
            for i, doc in enumerate(result["source_documents"], 1):
                st.markdown(f"**সোর্স {i}:**")
                st.text(doc.page_content[:300] + "...")
else:
    st.info("👆 প্রথমে একটি PDF ফাইল আপলোড করুন")
```

## চালানোর নিয়ম

```bash
streamlit run app.py
```

এটি চালানোর পর ব্রাউজারে একটি লিংক (সাধারণত `http://localhost:8501`) খুলে যাবে।

## অ্যাপে যা যা করা যাবে

| ফিচার | বিবরণ |
|---|---|
| 📤 PDF আপলোড | সরাসরি ব্রাউজার থেকে ফাইল সিলেক্ট করা |
| ⚙️ মডেল সিলেকশন | `llama3`, `phi3`, `mistral` থেকে বেছে নেওয়া |
| 🎛️ Chunk size ও k | স্লাইডার দিয়ে সহজে পরিবর্তন |
| ❓ প্রশ্ন-উত্তর | টেক্সট বক্সে প্রশ্ন লিখলেই উত্তর |
| 📄 সোর্স দেখা | উত্তর কোথা থেকে এসেছে তা expand করে দেখা |

## মনে রাখার বিষয়

- **Ollama আগে থেকে চালু থাকতে হবে** ব্যাকগ্রাউন্ডে (ইনস্টলের পর এমনিতেই চলে)
- সাইডবারে যে মডেল সিলেক্ট করবেন, সেটা আগেই `ollama pull <model_name>` দিয়ে ডাউনলোড করা থাকতে হবে
- প্রতিবার নতুন PDF আপলোড করলে আবার প্রসেস হবে (এটাকে চাইলে persistent storage দিয়েও করা যায়)

চাইলে আমি এই কোডটা সরাসরি একটি ফাইল (`app.py`) বানিয়ে আপনাকে ডাউনলোড লিংক দিতে পারি — চান কি?

