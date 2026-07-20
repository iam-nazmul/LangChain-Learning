# Vector Stores

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