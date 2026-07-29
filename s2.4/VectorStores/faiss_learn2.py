# pip install langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers

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