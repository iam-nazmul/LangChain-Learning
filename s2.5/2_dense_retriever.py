"""
২. Dense Retriever উদাহরণ (Embedding/Semantic ভিত্তিক)
------------------------------------------------------------
Dense Retriever শব্দের সরাসরি মিল না খুঁজে, "অর্থগত" (semantic) মিল খোঁজে।
অর্থাৎ, দুইটা বাক্যে একই শব্দ না থাকলেও যদি অর্থ কাছাকাছি হয়, তাহলেও খুঁজে পাবে।

বাস্তব প্রোডাকশনে সাধারণত এভাবে করা হয়:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")   # pretrained dense embedding model
    doc_embeddings = model.encode(documents)
    query_embedding = model.encode([query])

কিন্তু এখানে ইন্টারনেট থেকে বড় pretrained model ডাউনলোড করা সম্ভব নয় বলে,
আমরা TF-IDF + SVD (LSA - Latent Semantic Analysis) ব্যবহার করছি —
এটাও একটি বাস্তব dense/semantic embedding পদ্ধতি (word co-occurrence থেকে অর্থ শেখে)।
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class DenseRetriever:
    def __init__(self, documents: list[str], n_components: int = 4):
        self.documents = documents

        # ধাপ ১: প্রথমে TF-IDF vector বানানো হচ্ছে
        self.vectorizer = TfidfVectorizer()
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # ধাপ ২: SVD দিয়ে dimension কমিয়ে dense/semantic vector বানানো হচ্ছে
        # (এটাই মূলত "embedding" — শব্দের বদলে অর্থের representation)
        n_components = min(n_components, min(tfidf_matrix.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.doc_embeddings = self.svd.fit_transform(tfidf_matrix)

    def retrieve(self, query: str, top_k: int = 3):
        # প্রশ্নকেও একই embedding space-এ রূপান্তর করা হচ্ছে
        query_tfidf = self.vectorizer.transform([query])
        query_embedding = self.svd.transform(query_tfidf)

        # semantic vector-এর মধ্যে cosine similarity বের করা
        scores = cosine_similarity(query_embedding, self.doc_embeddings).flatten()
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

    print("===== Dense (LSA/SVD) Retriever =====")
    for r in DenseRetriever(chunks).retrieve(query):
        print(f"  - [score: {r['score']}] {r['chunk']}")
