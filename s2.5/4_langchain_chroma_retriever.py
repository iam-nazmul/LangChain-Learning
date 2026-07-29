"""
LangChain + ChromaDB দিয়ে Dense Retriever (প্রোডাকশন-স্টাইল)
------------------------------------------------------------------
এটাই আসলে আগের ৩টা উদাহরণের "বাস্তব প্রোডাকশন সংস্করণ" —
নিজে থেকে cosine similarity লেখার বদলে, LangChain + Chroma
vector database ব্যবহার করে পুরো কাজটা করা হচ্ছে (Chroma নিজেই
similarity search, storage, filtering ইত্যাদি হ্যান্ডেল করে)।

⚠️ গুরুত্বপূর্ণ নোট:
এই sandbox environment-এ Hugging Face (huggingface.co) বা OpenAI API
থেকে pretrained embedding model ডাউনলোড/কল করা সম্ভব না (নেটওয়ার্ক restriction)।

তাই এখানে একটা "CustomEmbeddings" ক্লাস বানানো হয়েছে (TF-IDF + SVD দিয়ে),
যেটা LangChain-এর Embeddings ইন্টারফেস মেনে চলে। আপনার নিজের মেশিনে/সার্ভারে
রান করলে নিচের যেকোনো একটা real embedding ব্যবহার করবেন (কমেন্টে দেওয়া আছে):

    # OpenAI embedding ব্যবহার করতে চাইলে:
    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # অথবা লোকাল/ফ্রি Hugging Face embedding ব্যবহার করতে চাইলে:
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

নিচের CustomEmbeddings ক্লাসটা শুধু ঐ real embedding-এর জায়গায়
"drop-in replacement" হিসেবে বসানো হয়েছে, বাকি পুরো pipeline
(text splitting, Chroma storage, retriever, similarity search)
হুবহু একই থাকবে আসল embedding model বসালেও।
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import numpy as np


# ----------------------------------------------------------------------
# ধাপ ০: Custom Embedding ক্লাস (LangChain-এর Embeddings ইন্টারফেস মেনে)
# ----------------------------------------------------------------------
class CustomEmbeddings(Embeddings):
    """
    LangChain-এর যেকোনো vector store (Chroma, FAISS, Pinecone ইত্যাদি)-এর
    সাথে কাজ করার জন্য শুধু দুইটা মেথড লাগে:
        - embed_documents(texts) -> List[List[float]]
        - embed_query(text)      -> List[float]
    """

    def __init__(self, documents: List[str], n_components: int = 4):
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        n_components = min(n_components, min(tfidf_matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.svd.fit(tfidf_matrix)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        tfidf = self.vectorizer.transform(texts)
        vectors = self.svd.transform(tfidf)
        return vectors.tolist()

    def embed_query(self, text: str) -> List[float]:
        tfidf = self.vectorizer.transform([text])
        vector = self.svd.transform(tfidf)
        return vector[0].tolist()


if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # ধাপ ১: মূল ডকুমেন্ট (এখনো chunk করা হয়নি)
    # ----------------------------------------------------------------------
    raw_text = """
বাংলাদেশের রাজধানী ঢাকা, যা বুড়িগঙ্গা নদীর তীরে অবস্থিত।
RAG (Retrieval-Augmented Generation) হলো একটি কৌশল যেখানে LLM বাইরের ডেটা থেকে তথ্য খুঁজে উত্তর দেয়।
Retriever একটি প্রশ্নের সাথে মিল রেখে প্রাসঙ্গিক chunk খুঁজে বের করে।
পদ্মা সেতু বাংলাদেশের একটি গুরুত্বপূর্ণ অবকাঠামো প্রকল্প।
Embedding মডেল টেক্সটকে সংখ্যার ভেক্টরে রূপান্তর করে, যাতে semantic মিল বের করা যায়।
Vector database যেমন Pinecone, Weaviate, ChromaDB ব্যবহার করে embedding সংরক্ষণ করা হয়।
"""

    # ----------------------------------------------------------------------
    # ধাপ ২: Chunking — LangChain-এর TextSplitter দিয়ে টেক্সট ভাগ করা
    # ----------------------------------------------------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,      # প্রতিটা chunk সর্বোচ্চ কত character
        chunk_overlap=20,    # পরপর chunk-এ কিছুটা overlap রাখা (context না হারানোর জন্য)
        separators=["\n", "।"],   # শুধু লাইন-ব্রেক আর বাক্যের শেষে (।) ভাঙা হবে
    )
    chunks = [c.strip() for c in splitter.split_text(raw_text) if c.strip()]
    documents = [Document(page_content=c) for c in chunks]

    print(f"মোট {len(chunks)}টা chunk তৈরি হয়েছে:\n")
    for i, c in enumerate(chunks):
        print(f"  [{i}] {c}")

    # ----------------------------------------------------------------------
    # ধাপ ৩: Embedding তৈরি + Chroma vector store-এ ইনডেক্স করা
    # ----------------------------------------------------------------------
    embeddings = CustomEmbeddings(chunks)

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="bangla_rag_demo",
    )

    # ----------------------------------------------------------------------
    # ধাপ ৪: Retriever তৈরি (LangChain-এর স্ট্যান্ডার্ড ইন্টারফেস)
    # ----------------------------------------------------------------------
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # ----------------------------------------------------------------------
    # ধাপ ৫: প্রশ্ন দিয়ে অনুসন্ধান
    # ----------------------------------------------------------------------
    query = "Retriever কীভাবে কাজ করে?"
    results = retriever.invoke(query)

    print(f"\nপ্রশ্ন: {query}\n")
    print("Chroma থেকে পাওয়া সবচেয়ে প্রাসঙ্গিক chunk গুলো:")
    for r in results:
        print(f"  - {r.page_content}")

    # score সহ দেখতে চাইলে similarity_search_with_score ব্যবহার করা যায়
    print("\n(score সহ)")
    scored_results = vectorstore.similarity_search_with_score(query, k=3)
    for doc, score in scored_results:
        print(f"  - [distance: {round(score, 4)}] {doc.page_content}")
