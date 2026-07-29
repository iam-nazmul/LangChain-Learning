from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# ১. Pinecone client init (API key দিয়ে)
pc = Pinecone(api_key="YOUR_API_KEY")

# ২. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ৩. Index তৈরি (cloud-এ, একবারই করতে হয়)
index_name = "my-docs"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# ৪. ডকুমেন্ট এম্বেড করে যোগ করা (upsert)
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]
embeddings = model.encode(documents)

index.upsert(vectors=[
    (str(i), embeddings[i].tolist(), {"text": documents[i]})
    for i in range(len(documents))
])

# ৫. Query করা
query_vector = model.encode("vehicle কেনার উপায়").tolist()
results = index.query(vector=query_vector, top_k=1, include_metadata=True)

print("সবচেয়ে relevant ডকুমেন্ট:", results["matches"][0]["metadata"]["text"])