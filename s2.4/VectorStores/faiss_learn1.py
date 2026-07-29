'''

লক্ষ্যণীয় পার্থক্য (Chroma vs FAISS)
Chroma: documents/metadata নিজে থেকে সংরক্ষণ করে, embedding মডেলও নিজে হ্যান্ডেল করে দেয়।
FAISS: শুধু vector সংরক্ষণ ও দ্রুত search করে — embedding বানানো, original টেক্সট ম্যাপ করে রাখা (যেমন documents[indices[0][0]] আমরা নিজে করলাম) — এসব আপনাকে নিজে ম্যানেজ করতে হয়।

'''


import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ১. Embedding model লোড করা
model = SentenceTransformer('all-MiniLM-L6-v2')

# ২. ডকুমেন্টগুলো
documents = ["গাড়ি কেনার নিয়ম", "রান্নার রেসিপি", "প্রোগ্রামিং শেখা"]

# ৩. টেক্সট -> vector (embedding) এ রূপান্তর
embeddings = model.encode(documents)
embeddings = np.array(embeddings).astype('float32')

# ৪. FAISS index তৈরি করা (Euclidean distance ভিত্তিক)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)

# ৫. Vector গুলো index-এ যোগ করা
index.add(embeddings)

# ৬. Query করা
query = ["vehicle কেনার উপায়"]
query_vector = model.encode(query).astype('float32')

k = 1  # সবচেয়ে কাছের ১টা রেজাল্ট চাই
distances, indices = index.search(query_vector, k)

print("সবচেয়ে relevant ডকুমেন্ট:", documents[indices[0][0]])

