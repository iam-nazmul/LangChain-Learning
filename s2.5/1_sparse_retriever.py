"""
১. Sparse Retriever উদাহরণ (Keyword-ভিত্তিক)
------------------------------------------------
Sparse Retriever শব্দের সরাসরি মিল (exact/keyword match) খোঁজে।
এখানে দুইটা জনপ্রিয় পদ্ধতি দেখানো হলো: TF-IDF এবং BM25

- TF-IDF: শব্দের frequency + rarity বিবেচনা করে vector বানায়
- BM25: TF-IDF-এর উন্নত সংস্করণ, ডকুমেন্টের length normalize করে
  (আধুনিক keyword search ইঞ্জিন যেমন Elasticsearch এটাই ব্যবহার করে)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import numpy as np


class TfidfRetriever:
    """TF-IDF ভিত্তিক sparse retriever"""

    def __init__(self, documents: list[str]):
        self.documents = documents
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def retrieve(self, query: str, top_k: int = 3):
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.doc_vectors).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"chunk": self.documents[i], "score": round(float(scores[i]), 4)}
            for i in top_indices if scores[i] > 0
        ]


class BM25Retriever:
    """BM25 ভিত্তিক sparse retriever (Elasticsearch-এর মতো keyword search)"""

    def __init__(self, documents: list[str]):
        self.documents = documents
        # প্রতিটি ডকুমেন্টকে শব্দে ভাগ করা (tokenize) হচ্ছে
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

    def retrieve(self, query: str, top_k: int = 3):
        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"chunk": self.documents[i], "score": round(float(scores[i]), 4)}
            for i in top_indices if scores[i] > 0
        ]


if __name__ == "__main__":
    chunks = [
        "বাংলাদেশের রাজধানী ঢাকা, যা বুড়িগঙ্গা নদীর তীরে অবস্থিত।",
        "RAG হলো একটি কৌশল যেখানে LLM বাইরের ডেটা থেকে তথ্য খুঁজে উত্তর দেয়।",
        "Retriever একটি প্রশ্নের সাথে মিল রেখে প্রাসঙ্গিক chunk খুঁজে বের করে।",
        "পদ্মা সেতু বাংলাদেশের একটি গুরুত্বপূর্ণ অবকাঠামো প্রকল্প।",
        "Embedding মডেল টেক্সটকে সংখ্যার ভেক্টরে রূপান্তর করে, যাতে semantic মিল বের করা যায়।",
        "Vector database যেমন Pinecone, Weaviate, ChromaDB ব্যবহার করে embedding সংরক্ষণ করা হয়।",
    ]
    query = "Retriever কীভাবে কাজ করে?"

    print("===== TF-IDF Retriever =====")
    for r in TfidfRetriever(chunks).retrieve(query):
        print(f"  - [score: {r['score']}] {r['chunk']}")

    print("\n===== BM25 Retriever =====")
    for r in BM25Retriever(chunks).retrieve(query):
        print(f"  - [score: {r['score']}] {r['chunk']}")
