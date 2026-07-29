import os
from pinecone import Pinecone, IntegratedSpec, EmbedConfig
from dotenv import load_dotenv



load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# ১. Client শুরু করা
pc = Pinecone(api_key=PINECONE_API_KEY)



# pc = Pinecone(api_key="YOUR_API_KEY")

index_name = "llama-text-embed-v2-index"

# ইনডেক্স আগে থেকে না থাকলে তৈরি করা হচ্ছে (integrated embedding সহ)
if not pc.indexes.exists(index_name):
    pc.indexes.create(
        name=index_name,
        spec=IntegratedSpec(
            cloud="aws",
            region="us-east-1",
            embed=EmbedConfig(
                model="llama-text-embed-v2",
                field_map={"text": "text"},
            ),
        ),
    )

index = pc.index(index_name)

# Because your index is integrated with a hosted embedding model, you provide inputs as text 
# and Pinecone converts them to dense vectors automatically.
data = [
    {"id": "vec1", "text": "Apple is a popular fruit known for its sweetness and crisp texture."},
    {"id": "vec2", "text": "The tech company Apple is known for its innovative products like the iPhone."},
    {"id": "vec3", "text": "Many people enjoy eating apples as a healthy snack."},
    {"id": "vec4", "text": "Apple Inc. has revolutionized the tech industry with its sleek designs and user-friendly interfaces."},
    {"id": "vec5", "text": "An apple a day keeps the doctor away, as the saying goes."},
    {"id": "vec6", "text": "Apple Computer Company was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne as a partnership."}
]

index.upsert_records(
    namespace="example-namespace",
    records=data
)




# ৪. Query করা (Pinecone নিজেই query text embed করে খুঁজবে)
results = index.search(
    namespace="example-namespace",
    top_k=2,
    inputs={"text": "Macbook m5 processor"}
)

for hit in results["result"]["hits"]:
    print(hit["id"], "-", hit["fields"]["text"])