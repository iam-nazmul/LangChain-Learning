# Vector Stores

import chromadb

# ১. Client তৈরি করা (লোকাল ফোল্ডারে ডেটা সেভ হবে)
client = chromadb.PersistentClient(path="./my_chroma_db")

# ২. একটি Collection তৈরি করা (এটা অনেকটা SQL-এর "table"-এর মতো)
collection = client.get_or_create_collection(name="my_docs")

# ৩. ডেটা/ডকুমেন্ট যোগ করা
collection.add(
    ids=["doc1", "doc2", "doc3"],  # প্রতিটি ডকুমেন্টের জন্য ইউনিক আইডি
    documents=[
        "বাংলাদেশের রাজধানী ঢাকা",
        "পিথন একটি জনপ্রিয় প্রোগ্রামিং ভাষা",
        "ভেক্টর ডেটাবেস সেমান্টিক সার্চের জন্য ব্যবহৃত হয়"
    ]
)

# ৪. সার্চ করা (Query)
results = collection.query(
    query_texts=["বাংলাদেশ সম্পর্কে কিছু বলো"],
    n_results=2  # সবচেয়ে কাছের ২টি ফলাফল
)

# print(results)



'''
results = {
    'ids': [['doc1', 'doc2']], 
    'embeddings': None, 
    'documents': [['বাংলাদেশের রাজধানী ঢাকা', 'পিথন একটি জনপ্রিয় প্রোগ্রামিং ভাষা']], 
    'uris': None,
    'included': ['metadatas', 'documents', 'distances'], 
    'data': None, 
    'metadatas': [[None, None]], 
    'distances': [[0.158624529838562, 0.3457670211791992]]
}
'''


# ----------------- মেটাডেটা সহ উদাহরণ (বাস্তব ব্যবহার) --------------------------
collection.add(
    documents=["ঢাকা শহরের ট্রাফিক সমস্যা নিয়ে একটি প্রতিবেদন"],
    metadatas=[{"category": "news", "year": 2025}],
    ids=["doc4"]
)

# মেটাডেটা দিয়ে ফিল্টার করে সার্চ
results = collection.query(
    query_texts=["ঢাকার সমস্যা"],
    n_results=2,
    where={"category": "news"}  # শুধু "news" ক্যাটাগরির মধ্যে খুঁজবে
)

print(results)


'''
results = {
    'ids': [['doc4']], 
    'embeddings': None, 
    'documents': [['ঢাকা শহরের ট্রাফিক সমস্যা নিয়ে একটি প্রতিবেদন']], 
    'uris': None, 
    'included': ['metadatas', 'documents', 'distances'], 
    'data': None, 
    'metadatas': [[{'category': 'news', 'year': 2025}]], 
    'distances': [[0.49445486068725586]]
}
'''

# ---------------------------------------------------------------