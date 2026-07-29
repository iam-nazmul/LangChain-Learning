'''

খুব সংক্ষিপ্ত উদাহরণ (Python, Qdrant দিয়ে)

Qdrant একটা আলাদা server/database হিসেবে চলে (local বা cloud), তাই প্রথমে সেটা চালু থাকতে হয়। সহজে টেস্ট করতে in-memory mode ব্যবহার করছি (কোনো server লাগবে না):
'''


from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

# ১. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ২. Qdrant client (in-memory — শুধু টেস্টের জন্য)
client = QdrantClient(":memory:")

# ৩. Collection তৈরি
client.create_collection(
    collection_name="my_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# ৪. ডকুমেন্টগুলো এম্বেড করে যোগ করা
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
query_vector = model.encode("গাড়ি নিয়ম").tolist()
results = client.query_points(collection_name="my_docs", query=query_vector, limit=1)

print("সবচেয়ে relevant ডকুমেন্ট:", results.points[0].payload["text"])


'''
ইনস্টল
bash
pip install qdrant-client sentence-transformers

আগের গুলোর সাথে পার্থক্য
FAISS: শুধু একটা লাইব্রেরি, কোনো server নেই, সব কিছু একই প্রোগ্রামের মেমরিতে থাকে।
Qdrant: এটা একটা client-server ডাটাবেস — :memory: দিয়ে টেস্ট করা গেলেও, প্রোডাকশনে সাধারণত আলাদা Qdrant server (Docker বা cloud-এ) চালিয়ে QdrantClient(url="http://localhost:6333") দিয়ে কানেক্ট করা হয়। এতে payload (metadata) সহ ডাটা persist হয়ে থাকে, filter করে খোঁজা যায় (যেমন: শুধু নির্দিষ্ট category-র ডকুমেন্ট খুঁজো), আর একসাথে অনেক ইউজার/অ্যাপ থেকে access করা যায়।
'''