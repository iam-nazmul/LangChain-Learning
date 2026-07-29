# খুব সংক্ষিপ্ত উদাহরণ (Python, Pinecone দিয়ে)

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# ১. Client শুরু করা
pc = Pinecone(api_key=PINECONE_API_KEY)

# ২. Index তৈরি করা (না থাকলে) — Pinecone নিজেই embedding বানাবে
index_name = "developer-quickstart-py"

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "chunk_text"}
        }
    )

index = pc.Index(index_name)

# ৩. ডকুমেন্ট upsert করা (namespace-এর ভিতরে)
# `chunk_text` অটো embed হয়ে dense vector হবে, `category` metadata হিসেবে থাকবে
namespace = "example-namespace"

index.upsert_records(
    namespace=namespace,
    records=[
        {
            "_id": "rec1",
            "chunk_text": "Apples are a great source of dietary fiber, which supports digestion and helps maintain a healthy gut.",
            "category": "digestive system",
        },
        {
            "_id": "rec2",
            "chunk_text": "Apples originated in Central Asia and have been cultivated for thousands of years, with over 7,500 varieties available today.",
            "category": "cultivation",
        },
        {
            "_id": "rec3",
            "chunk_text": "Rich in vitamin C and other antioxidants, apples contribute to immune health and may reduce the risk of chronic diseases.",
            "category": "immune system",
        },
        {
            "_id": "rec4",
            "chunk_text": "The high fiber content in apples can also help regulate blood sugar levels, making them a favorable snack for people with diabetes.",
            "category": "endocrine system",
        },
    ]
)

# ৪. Query করা (Pinecone নিজেই query text embed করে খুঁজবে)
results = index.search(
    namespace=namespace,
    top_k=2,
    inputs={"text": "immune system health benefits"}
)

for hit in results["result"]["hits"]:
    print(hit["id"], "-", hit["fields"]["chunk_text"])

'''
ইনস্টল
bash
pip install pinecone python-dotenv

.env ফাইলে
PINECONE_API_KEY=your_api_key_here

আগের গুলোর সাথে পার্থক্য
Chroma: লোকাল, in-process, কোনো server/API key লাগে না।
FAISS: শুধু লাইব্রেরি, নিজে embedding বানাতে হয়, persistence নিজেকে সামলাতে হয়।
Qdrant: client-server, self-host বা cloud, filtering সহ শক্তিশালী।
Pinecone: fully-managed cloud vector DB — embedding, indexing, scaling সব ওরা সামলায়, শুধু API key লাগে।
'''
