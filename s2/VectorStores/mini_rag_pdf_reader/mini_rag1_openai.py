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