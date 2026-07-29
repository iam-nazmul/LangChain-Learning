"""
সহজ Retriever উদাহরণ (Simple Vector/Sparse Retriever Example)
--------------------------------------------------------------
এখানে আমরা বাহ্যিক লাইব্রেরি (LangChain/vector DB) ছাড়াই দেখাচ্ছি,
কিভাবে একটি প্রশ্নের (query) সাথে সবচেয়ে প্রাসঙ্গিক chunk খুঁজে বের করা যায়।

পদ্ধতি: TF-IDF + Cosine Similarity (Sparse Retriever)
এটি সহজে বোঝার জন্য ভালো — আসল প্রোডাকশন সিস্টেমে সাধারণত
sentence-transformers বা OpenAI embedding দিয়ে "Dense Retriever" বানানো হয়,
কিন্তু মূল ধারণা (query -> similarity -> top-k chunk) একই থাকে।
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SimpleRetriever:
    def __init__(self, documents: list[str]):
        """
        documents: chunk-এ ভাগ করা টেক্সটের লিস্ট
        """
        self.documents = documents
        # TF-IDF vectorizer তৈরি করা হচ্ছে
        self.vectorizer = TfidfVectorizer()
        # সব ডকুমেন্টকে একসাথে fit + transform করে vector বানানো হচ্ছে
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def retrieve(self, query: str, top_k: int = 3):
        """
        query: ব্যবহারকারীর প্রশ্ন
        top_k: কয়টা সবচেয়ে প্রাসঙ্গিক chunk ফেরত দিতে হবে
        """
        # প্রশ্নটিকেও একই vector space-এ রূপান্তর করা হচ্ছে
        query_vector = self.vectorizer.transform([query])

        # প্রশ্নের vector-এর সাথে প্রতিটি chunk vector-এর cosine similarity বের করা
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()

        # সবচেয়ে বেশি similarity থাকা chunk গুলোর index বের করা (বড় থেকে ছোট)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # ফলাফল হিসেবে chunk এবং তার similarity score রিটার্ন করা
        results = [
            {"chunk": self.documents[i], "score": round(float(similarities[i]), 4)}
            for i in top_indices
            if similarities[i] > 0  # একদম অপ্রাসঙ্গিক (score=0) বাদ দেওয়া
        ]
        return results


if __name__ == "__main__":
    # ------------------------------
    # ধাপ ১: ডকুমেন্ট থেকে chunk তৈরি (এখানে আগে থেকেই ভাগ করা আছে ধরে নিচ্ছি)
    # ------------------------------
    chunks = [
        "বাংলাদেশের রাজধানী ঢাকা, যা বুড়িগঙ্গা নদীর তীরে অবস্থিত।",
        "RAG (Retrieval-Augmented Generation) হলো একটি কৌশল যেখানে LLM বাইরের ডেটা থেকে তথ্য খুঁজে উত্তর দেয়।",
        "Retriever একটি প্রশ্নের সাথে মিল রেখে প্রাসঙ্গিক chunk খুঁজে বের করে।",
        "পদ্মা সেতু বাংলাদেশের একটি গুরুত্বপূর্ণ অবকাঠামো প্রকল্প।",
        "Embedding মডেল টেক্সটকে সংখ্যার ভেক্টরে রূপান্তর করে, যাতে semantic মিল বের করা যায়।",
        "Vector database যেমন Pinecone, Weaviate, ChromaDB ব্যবহার করে embedding সংরক্ষণ করা হয়।",
    ]

    # ------------------------------
    # ধাপ ২: Retriever তৈরি (Indexing)
    # ------------------------------
    retriever = SimpleRetriever(chunks)

    # ------------------------------
    # ধাপ ৩: প্রশ্ন দিয়ে অনুসন্ধান (Retrieval)
    # ------------------------------
    query = "Retriever কীভাবে কাজ করে?"
    results = retriever.retrieve(query, top_k=3)

    print(f"প্রশ্ন: {query}\n")
    print("সবচেয়ে প্রাসঙ্গিক chunk গুলো:")
    for r in results:
        print(f"  - [score: {r['score']}] {r['chunk']}")
