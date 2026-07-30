"""
LangChain + ChromaDB দিয়ে Hybrid Retriever (Sparse + Dense)
------------------------------------------------------------------
Hybrid Retriever = BM25Retriever (sparse/keyword) + Chroma vectorstore
retriever (dense/semantic), যেটা LangChain-এর `EnsembleRetriever` দিয়ে
weighted combination করে চূড়ান্ত ranking তৈরি করে।

EnsembleRetriever ভিতরে ভিতরে Reciprocal Rank Fusion (RRF) ব্যবহার করে
দুইটা retriever-এর ফলাফলকে merge করে — অর্থাৎ প্রতিটা retriever আলাদাভাবে
তার নিজের ranking দেয়, তারপর সেই rank-গুলোকে ফিউজ করে একটা চূড়ান্ত
ranking বানানো হয় (raw score merge না করে rank-ভিত্তিক merge, তাই
দুই ভিন্ন স্কেলের score (BM25 vs cosine) নিয়ে চিন্তা করতে হয় না)।

⚠️ নোট: আগের কোডের মতোই, এখানে dense অংশের জন্য pretrained embedding
(OpenAI/HuggingFace) না থাকায় TF-IDF+SVD ভিত্তিক CustomEmbeddings
ব্যবহার করা হয়েছে (কমেন্টে real embedding ব্যবহারের নির্দেশনা আছে)।
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


# ----------------------------------------------------------------------
# Custom Embedding ক্লাস (dense অংশের জন্য) — আগের কোডের মতোই
# ----------------------------------------------------------------------
class CustomEmbeddings(Embeddings):
    """
    আসল প্রোডাকশনে এটার বদলে বসবে:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    অথবা:
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    """

    def __init__(self, documents: List[str], n_components: int = 4):
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        n_components = min(n_components, min(tfidf_matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.svd.fit(tfidf_matrix)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        tfidf = self.vectorizer.transform(texts)
        return self.svd.transform(tfidf).tolist()

    def embed_query(self, text: str) -> List[float]:
        tfidf = self.vectorizer.transform([text])
        return self.svd.transform(tfidf)[0].tolist()


if __name__ == "__main__":
    # ----------------------------------------------------------------------
    # ধাপ ১: ডকুমেন্ট প্রস্তুতি + Chunking
    # ----------------------------------------------------------------------
    raw_text = """
    বাংলাদেশের রাজধানী ঢাকা, যা বুড়িগঙ্গা নদীর তীরে অবস্থিত।
    RAG (Retrieval-Augmented Generation) হলো একটি কৌশল যেখানে LLM বাইরের ডেটা থেকে তথ্য খুঁজে উত্তর দেয়।
    Retriever একটি প্রশ্নের সাথে মিল রেখে প্রাসঙ্গিক chunk খুঁজে বের করে।
    পদ্মা সেতু বাংলাদেশের একটি গুরুত্বপূর্ণ অবকাঠামো প্রকল্প।
    Embedding মডেল টেক্সটকে সংখ্যার ভেক্টরে রূপান্তর করে, যাতে semantic মিল বের করা যায়।
    Vector database যেমন Pinecone, Weaviate, ChromaDB ব্যবহার করে embedding সংরক্ষণ করা হয়।
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=20,
        separators=["\n", "।"],
    )
    chunks = [c.strip() for c in splitter.split_text(raw_text) if c.strip()]
    documents = [Document(page_content=c) for c in chunks]

    print(f"মোট {len(chunks)}টা chunk তৈরি হয়েছে।\n")

    # ----------------------------------------------------------------------
    # ধাপ ২: Sparse Retriever (BM25) তৈরি
    # ----------------------------------------------------------------------
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 3  # top-3 রেজাল্ট দেবে

    # ----------------------------------------------------------------------
    # ধাপ ৩: Dense Retriever (Chroma vectorstore) তৈরি
    # ----------------------------------------------------------------------
    embeddings = CustomEmbeddings(chunks)
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="bangla_hybrid_demo",
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # ----------------------------------------------------------------------
    # ধাপ ৪: EnsembleRetriever দিয়ে দুইটা মিলিয়ে Hybrid Retriever বানানো
    # ----------------------------------------------------------------------
    hybrid_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, dense_retriever],
        weights=[0.5, 0.5],  # sparse আর dense-কে সমান গুরুত্ব দেওয়া হচ্ছে
        # weights=[0.7, 0.3]  # চাইলে keyword-এর দিকে বেশি ঝোঁক দেওয়া যায়
        # weights=[0.3, 0.7]  # অথবা semantic/অর্থগত মিলের দিকে বেশি ঝোঁক
    )

    # ----------------------------------------------------------------------
    # ধাপ ৫: প্রশ্ন দিয়ে অনুসন্ধান
    # ----------------------------------------------------------------------
    query = "Retriever কীভাবে কাজ করে?"

    print(f"প্রশ্ন: {query}\n")

    print("===== শুধু BM25 (sparse) =====")
    for doc in bm25_retriever.invoke(query):
        print(f"  - {doc.page_content}")

    print("\n===== শুধু Chroma (dense) =====")
    for doc in dense_retriever.invoke(query):
        print(f"  - {doc.page_content}")

    print("\n===== Hybrid (BM25 + Chroma, fused via EnsembleRetriever) =====")
    for doc in hybrid_retriever.invoke(query):
        print(f"  - {doc.page_content}")
