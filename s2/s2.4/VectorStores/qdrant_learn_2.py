from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# ১. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# # ২. Local path-এ সেভ হবে (persistent — প্রোগ্রাম বন্ধ করলেও ডাটা থাকবে)
# client = QdrantClient(path="./qdrant_local_db")


# Option ২: Docker দিয়ে Local Server চালিয়ে (Production-এর মতো)

# প্রথমে Docker-এ Qdrant চালু করুন:


# docker run -p 6333:6333 qdrant/qdrant

# ৬৩৩৩ পোর্টে চলা local server-এর সাথে কানেক্ট
client = QdrantClient(url="http://localhost:6333")



# ৩. Collection তৈরি (আগে থাকলে স্কিপ করাই ভালো)
if not client.collection_exists("my_docs"):
    client.create_collection(
        collection_name="my_docs",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

# ৪. ডকুমেন্ট এম্বেড করে যোগ করা
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]
embeddings = model.encode(documents)

client.upsert(
    collection_name="my_docs",
    points=[
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": documents[i]})
        for i in range(len(documents))
    ]
)

# ৫. Query করা
query_vector = model.encode("vehicle কেনার উপায়").tolist()
results = client.query_points(collection_name="my_docs", query=query_vector, limit=1)

print("সবচেয়ে relevant ডকুমেন্ট:", results.points[0].payload["text"])