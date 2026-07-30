"""
৩. Hybrid Retriever উদাহরণ (Sparse + Dense একসাথে)
------------------------------------------------------------
Hybrid Retriever দুইটা পদ্ধতিরই সুবিধা নেয়:
    - Sparse (BM25): exact keyword/নাম/সংখ্যা মিলে ভালো কাজ করে
    - Dense (embedding): সমার্থক শব্দ ও অর্থগত মিল বুঝতে পারে

দুইটা স্কোরকে normalize করে একটা weighted combination (alpha) দিয়ে
মিলিয়ে চূড়ান্ত ranking তৈরি করা হয়।
"""

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class HybridRetriever:
    def __init__(self, documents: list[str], n_components: int = 4, alpha: float = 0.5):
        """
        alpha: sparse আর dense score-এর ভারসাম্য (weight)
               alpha=1.0 -> শুধু sparse, alpha=0.0 -> শুধু dense
        """
        self.documents = documents
        self.alpha = alpha

        # ---- Sparse (BM25) সেটআপ ----
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)

        # ---- Dense (TF-IDF + SVD) সেটআপ ----
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        n_components = min(n_components, min(tfidf_matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.doc_embeddings = self.svd.fit_transform(tfidf_matrix)

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        """স্কোরগুলোকে ০-১ এর মধ্যে normalize করা হচ্ছে, যাতে দুই ধরনের
        score (sparse vs dense) ন্যায্যভাবে যোগ করা যায়"""
        if scores.max() - scores.min() == 0:
            return np.zeros_like(scores)
        return (scores - scores.min()) / (scores.max() - scores.min())

    def retrieve(self, query: str, top_k: int = 3):
        # ---- Sparse score ----
        sparse_scores = np.array(self.bm25.get_scores(query.split()))
        sparse_scores = self._normalize(sparse_scores)

        # ---- Dense score ----
        query_tfidf = self.vectorizer.transform([query])
        query_embedding = self.svd.transform(query_tfidf)
        dense_scores = cosine_similarity(query_embedding, self.doc_embeddings).flatten()
        dense_scores = self._normalize(dense_scores)

        # ---- দুইটা মিলিয়ে চূড়ান্ত স্কোর ----
        final_scores = self.alpha * sparse_scores + (1 - self.alpha) * dense_scores

        top_indices = np.argsort(final_scores)[::-1][:top_k]
        return [
            {
                "chunk": self.documents[i],
                "final_score": round(float(final_scores[i]), 4),
                "sparse": round(float(sparse_scores[i]), 4),
                "dense": round(float(dense_scores[i]), 4),
            }
            for i in top_indices if final_scores[i] > 0
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

    print("===== Hybrid Retriever (alpha=0.5) =====")
    for r in HybridRetriever(chunks, alpha=0.5).retrieve(query):
        print(
            f"  - [final: {r['final_score']} | sparse: {r['sparse']} | dense: {r['dense']}] "
            f"{r['chunk']}"
        )
