import chromadb

client = chromadb.Client()
collection = client.create_collection("my_docs")

# ডকুমেন্ট যোগ করা (Chroma নিজেই embedding বানাবে ডিফল্ট মডেল দিয়ে)
collection.add(
    documents=["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"],
    ids=["doc1", "doc2", "doc3"]
)

# খোঁজা
results = collection.query(
    query_texts=["গাড়ি কেনার উপায়"],
    n_results=1
)
print(results)  # doc1 সবচেয়ে বেশি relevant হিসেবে আসবে