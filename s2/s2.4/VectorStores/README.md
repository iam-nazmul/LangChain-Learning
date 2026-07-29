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




---
---
---
---
---
---


## Vector Stores কী?

Vector store হলো একটা বিশেষ ধরনের ডাটাবেস, যেটা সাধারণ টেক্সট বা নম্বরের বদলে **"vector"** (embedding) সংরক্ষণ করে এবং সেগুলোর মধ্যে **similarity (মিল)** খুঁজে বের করতে পারে — সাধারণ SQL ডাটাবেসের মতো exact match খোঁজে না।

### কেন দরকার হয়?

ধরুন আপনার কাছে ১০০০টা ডকুমেন্ট আছে, আর আপনি চান কোনো একটা প্রশ্নের উত্তরের জন্য সবচেয়ে relevant ডকুমেন্টগুলো খুঁজে বের করতে (এটাই RAG — Retrieval Augmented Generation এর মূল ভিত্তি)।

সাধারণ keyword search শুধু exact word match খোঁজে। কিন্তু আপনি চান **অর্থগত মিল (semantic similarity)**। যেমন:
- Query: "গাড়ি কেনার উপায়"
- Document: "কীভাবে একটা vehicle purchase করবেন"

শব্দ আলাদা, কিন্তু অর্থ একই। এটা করতে হলে টেক্সটকে সংখ্যার list (vector/embedding) এ রূপান্তর করতে হয়, আর সেই vector গুলোর মধ্যে দূরত্ব মেপে মিল বের করা হয়।

### কীভাবে কাজ করে (ধাপে ধাপে)

1. **Embedding তৈরি** — প্রতিটা টেক্সট/ডকুমেন্টকে একটা embedding model (যেমন OpenAI বা Cohere এর মডেল) দিয়ে একটা vector-এ রূপান্তর করা হয়। এই vector হলো শত শত সংখ্যার একটা array, যা টেক্সটের "অর্থ" ধারণ করে।
2. **Store করা** — এই vector গুলো vector store-এ সেভ করা হয়, সাথে original টেক্সটও (metadata হিসেবে)।
3. **Search করা** — যখন একটা নতুন query আসে, সেটাকেও একই মডেল দিয়ে vector-এ রূপান্তর করা হয়।
4. **Similarity বের করা** — সেই query vector-এর সাথে store-এ থাকা সব vector-এর দূরত্ব (সাধারণত Cosine Similarity বা Euclidean Distance) মাপা হয়, আর সবচেয়ে কাছাকাছি (similar) গুলো return করা হয়।

### জনপ্রিয় টুলগুলোর মধ্যে পার্থক্য

| টুল | ধরন | বৈশিষ্ট্য |
|---|---|---|
| **FAISS** | Library (Facebook) | শুধু in-memory, খুব দ্রুত, কিন্তু নিজে থেকে persistent storage/server নেই — নিজে সেটআপ করতে হয় |
| **Chroma** | ছোট local vector DB | সহজ, beginner-friendly, local ফাইলে সেভ হয়, ছোট প্রজেক্টের জন্য দারুণ |
| **Qdrant** | Production-grade DB | নিজের server চালানো যায় (open-source), filter/metadata সাপোর্ট ভালো, বড় স্কেলে কাজ করে |
| **Pinecone** | Managed cloud সার্ভিস | নিজে হোস্ট করতে হয় না, scale automatically হয়, কিন্তু paid service |

### ছোট বিষয়: কখন কোনটা বেছে নেবেন?

- শেখার জন্য বা ছোট প্রজেক্ট → **Chroma** বা **FAISS**
- প্রোডাকশনে নিজে হোস্ট করতে চান → **Qdrant**
- ম্যানেজড, স্কেলেবল সলিউশন চান, ইনফ্রা নিয়ে ভাবতে চান না → **Pinecone**

### খুব সংক্ষিপ্ত উদাহরণ (Python, Chroma দিয়ে)

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("my_docs")

# ডকুমেন্ট যোগ করা (Chroma নিজেই embedding বানাবে ডিফল্ট মডেল দিয়ে)
collection.add(
    documents=["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"],
    ids=["doc1", "doc2", "doc3"]
)

# খোঁজা
results = collection.query(
    query_texts=["vehicle কেনার উপায়"],
    n_results=1
)
print(results)  # doc1 সবচেয়ে বেশি relevant হিসেবে আসবে
```

চাইলে আমি এটাকে একটা visual diagram হিসেবেও দেখাতে পারি — যেখানে embedding তৈরি থেকে শুরু করে query আর similarity search পুরো প্রসেসটা flow-chart আকারে বোঝা যাবে। দেখতে চান?


---

## খুব সংক্ষিপ্ত উদাহরণ (Python, FAISS দিয়ে)

FAISS নিজে থেকে টেক্সট থেকে embedding বানায় না — আপনাকে আলাদা একটা embedding model ব্যবহার করতে হয় (এখানে সহজ উদাহরণের জন্য `sentence-transformers` ব্যবহার করছি)।

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ১. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ২. ডকুমেন্টগুলো
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]

# ৩. টেক্সট -> vector (embedding) এ রূপান্তর
embeddings = model.encode(documents)
embeddings = np.array(embeddings).astype('float32')

# ৪. FAISS index তৈরি করা (Euclidean distance ভিত্তিক)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# ৫. Vector গুলো index-এ যোগ করা
index.add(embeddings)

# ৬. Query করা
query = ["vehicle কেনার উপায়"]
query_vector = model.encode(query).astype('float32')

k = 1  # সবচেয়ে কাছের ১টা রেজাল্ট চাই
distances, indices = index.search(query_vector, k)

print("সবচেয়ে relevant ডকুমেন্ট:", documents[indices[0][0]])
```

### লক্ষ্যণীয় পার্থক্য (Chroma vs FAISS)

- **Chroma**: documents/metadata নিজে থেকে সংরক্ষণ করে, embedding মডেলও নিজে হ্যান্ডেল করে দেয়।
- **FAISS**: শুধু vector সংরক্ষণ ও দ্রুত search করে — embedding বানানো, original টেক্সট ম্যাপ করে রাখা (যেমন `documents[indices[0][0]]` আমরা নিজে করলাম) — এসব আপনাকে নিজে ম্যানেজ করতে হয়।

এই কারণেই FAISS-কে বলা হয় "library" (নিচু-স্তরের টুল), আর Chroma-কে বলা হয় "vector database" (উচ্চ-স্তরের, ready-to-use সলিউশন)।

---

## খুব সংক্ষিপ্ত উদাহরণ (Python, FAISS + Huggingface Embedding)

এখানে LangChain-এর মাধ্যমে Huggingface embedding মডেল ব্যবহার করে FAISS চালানো হচ্ছে (এটাই সবচেয়ে সহজ ও প্রচলিত উপায়):

```python
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ১. Huggingface embedding model লোড করা
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ২. ডকুমেন্টগুলো
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]

# ৩. FAISS vector store তৈরি (embedding + storage একসাথে হয়ে যাচ্ছে)
vector_store = FAISS.from_texts(documents, embeddings)

# ৪. Query করা (similarity search)
query = "vehicle কেনার উপায়"
results = vector_store.similarity_search(query, k=1)

print("সবচেয়ে relevant ডকুমেন্ট:", results[0].page_content)
```

### ইনস্টল করতে হবে

```bash
pip install langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers
```

### আগের raw FAISS উদাহরণের সাথে পার্থক্য

- **আগের উদাহরণে**: `sentence-transformers` দিয়ে সরাসরি embedding বানিয়ে, নিজে হাতে FAISS index (`IndexFlatL2`) তৈরি ও ম্যানেজ করতে হয়েছিল।
- **এখানে**: LangChain-এর `HuggingFaceEmbeddings` wrapper + `FAISS.from_texts()` ব্যবহার করায় embedding তৈরি, index বানানো, document-vector ম্যাপিং — সবকিছু automatically হয়ে যাচ্ছে। কোড অনেক ছোট ও পরিষ্কার হয়।

এটা মূলত RAG পাইপলাইন বানানোর সময় সবচেয়ে বেশি ব্যবহৃত প্যাটার্ন — কারণ পরে সহজেই `retriever = vector_store.as_retriever()` করে LLM-এর সাথে যুক্ত করা যায়।


---

## খুব সংক্ষিপ্ত উদাহরণ (Python, Qdrant দিয়ে)

Qdrant একটা আলাদা server/database হিসেবে চলে (local বা cloud), তাই প্রথমে সেটা চালু থাকতে হয়। সহজে টেস্ট করতে **in-memory mode** ব্যবহার করছি (কোনো server লাগবে না):

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

# ১. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ২. Qdrant client (in-memory — শুধু টেস্টের জন্য)
client = QdrantClient(":memory:")

# ৩. Collection তৈরি
client.create_collection(
    collection_name="my_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# ৪. ডকুমেন্টগুলো এম্বেড করে যোগ করা
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]
embeddings = model.encode(documents)

client.upsert(
    collection_name="my_docs",
    points=[
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": documents[i]})
        for i in range(len(documents))
    ]
)

# ৫. Query করা
query_vector = model.encode("vehicle কেনার উপায়").tolist()
results = client.search(collection_name="my_docs", query_vector=query_vector, limit=1)

print("সবচেয়ে relevant ডকুমেন্ট:", results[0].payload["text"])


'''


### ইনস্টল

```bash

```

### আগের গুলোর সাথে পার্থক্য

- **FAISS**: শুধু একটা লাইব্রেরি, কোনো server নেই, সব কিছু একই প্রোগ্রামের মেমরিতে থাকে।
- **Qdrant**: এটা একটা **client-server** ডাটাবেস — `:memory:` দিয়ে টেস্ট করা গেলেও, প্রোডাকশনে সাধারণত আলাদা Qdrant server (Docker বা cloud-এ) চালিয়ে `QdrantClient(url="http://localhost:6333")` দিয়ে কানেক্ট করা হয়। এতে `payload` (metadata) সহ ডাটা persist হয়ে থাকে, filter করে খোঁজা যায় (যেমন: শুধু নির্দিষ্ট category-র ডকুমেন্ট খুঁজো), আর একসাথে অনেক ইউজার/অ্যাপ থেকে access করা যায়।


---


## খুব সংক্ষিপ্ত উদাহরণ (Python, Pinecone দিয়ে)

Pinecone একটা **cloud-hosted managed service**, তাই প্রথমে [pinecone.io](https://www.pinecone.io) থেকে ফ্রি একাউন্ট খুলে **API key** নিতে হয়।

```python
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# ১. Pinecone client init (API key দিয়ে)
pc = Pinecone(api_key="YOUR_API_KEY")

# ২. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ৩. Index তৈরি (cloud-এ, একবারই করতে হয়)
index_name = "my-docs"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# ৪. ডকুমেন্ট এম্বেড করে যোগ করা (upsert)
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]
embeddings = model.encode(documents)

index.upsert(vectors=[
    (str(i), embeddings[i].tolist(), {"text": documents[i]})
    for i in range(len(documents))
])

# ৫. Query করা
query_vector = model.encode("vehicle কেনার উপায়").tolist()
results = index.query(vector=query_vector, top_k=1, include_metadata=True)

print("সবচেয়ে relevant ডকুমেন্ট:", results["matches"][0]["metadata"]["text"])
```

### ইনস্টল

```bash
pip install pinecone sentence-transformers
```

### আগের গুলোর সাথে পার্থক্য

| বিষয় | Qdrant (local) | Pinecone |
|---|---|---|
| হোস্টিং | নিজের কম্পিউটার/সার্ভার | সম্পূর্ণ Pinecone-এর cloud-এ |
| সেটআপ | Docker বা local file | শুধু API key |
| খরচ | ফ্রি (নিজের রিসোর্স ব্যবহার) | Free tier আছে, তবে স্কেল বাড়লে paid |
| Maintenance | নিজে ম্যানেজ করতে হয় | Pinecone নিজেই স্কেল/আপডেট/backup করে |

**সংক্ষেপে**: প্রোটোটাইপ/শেখার জন্য Chroma বা FAISS, নিজের ইনফ্রা কন্ট্রোল করতে চাইলে Qdrant, আর ইনফ্রা নিয়ে একদম মাথা ঘামাতে না চাইলে (production-ready, auto-scaling) Pinecone সবচেয়ে সহজ।


