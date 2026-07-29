# Retriever কী?

Retriever হলো একটি সিস্টেম যা RAG (Retrieval-Augmented Generation) পাইপলাইনে ব্যবহৃত হয়, যার কাজ হলো একটি প্রশ্ন (query) দেওয়া হলে, বিশাল ডেটাসেট বা ডকুমেন্ট থেকে সবচেয়ে প্রাসঙ্গিক তথ্যের টুকরো (chunk) খুঁজে বের করা।

## কীভাবে কাজ করে

**১. ডকুমেন্ট প্রস্তুতি (Indexing)**
- বড় ডকুমেন্টগুলোকে ছোট ছোট অংশে (chunk) ভাগ করা হয়
- প্রতিটি chunk-কে একটি embedding মডেল দিয়ে vector-এ রূপান্তর করা হয় (সংখ্যার একটি array যা অর্থ ধারণ করে)
- এই vector গুলো একটি vector database-এ সংরক্ষণ করা হয় (যেমন: Pinecone, Weaviate, ChromaDB)

**২. অনুসন্ধান (Retrieval)**
- ব্যবহারকারীর প্রশ্নটিকেও একই embedding মডেল দিয়ে vector-এ রূপান্তর করা হয়
- এরপর query vector-এর সাথে সবচেয়ে কাছাকাছি (similar) chunk vector গুলো খুঁজে বের করা হয় — সাধারণত cosine similarity বা dot product ব্যবহার করে
- সবচেয়ে প্রাসঙ্গিক top-k (যেমন ৩-৫টি) chunk রিটার্ন করা হয়

**৩. ব্যবহার**
- এই খুঁজে পাওয়া chunk গুলো LLM-এর প্রম্পটে context হিসেবে যোগ করা হয়, যাতে মডেল সঠিক ও সাম্প্রতিক তথ্যের ভিত্তিতে উত্তর দিতে পারে

## Retriever-এর প্রকারভেদ

| ধরন | বিবরণ |
|---|---|
| **Sparse Retriever** | keyword-ভিত্তিক (যেমন: BM25, TF-IDF) — শব্দের মিল খোঁজে |
| **Dense Retriever** | embedding-ভিত্তিক — অর্থগত (semantic) মিল খোঁজে |
| **Hybrid Retriever** | sparse + dense দুটোই মিলিয়ে ব্যবহার করে, ফলাফল আরও নির্ভুল হয় |

## কেন গুরুত্বপূর্ণ

Retriever ভালো না হলে LLM ভুল বা অপ্রাসঙ্গিক তথ্য পায়, ফলে উত্তরও ভুল হয়ে যেতে পারে (hallucination বাড়ে)। তাই RAG সিস্টেমে retriever-এর কার্যকারিতা পুরো পাইপলাইনের গুণমান নির্ধারণ করে।

আপনি কি চাইছেন আমি এটার একটা code example (যেমন Python-এ LangChain বা simple vector search) দেখিয়ে দিই?


---


তিনটা retriever-ের কোড বানিয়ে দিচ্ছি। **নোট:** Dense retriever-এর জন্য সাধারণত `sentence-transformers` দিয়ে বড় pretrained model (যেমন Hugging Face থেকে) ডাউনলোড করা হয়, কিন্তু এই sandbox environment-এ Hugging Face এক্সেস নেই। তাই আমি TF-IDF + **SVD (LSA - Latent Semantic Analysis)** ব্যবহার করে দেখাচ্ছি, যা একটি বাস্তব ও প্রচলিত dense/semantic embedding পদ্ধতি — concept একই থাকবে।সবগুলো ঠিকভাবে কাজ করছে।**ফলাফল বিশ্লেষণ:**

| Retriever | কী পেল | কেন |
|---|---|---|
| **TF-IDF** (sparse) | শুধু ১টা chunk | কারণ শুধু ঐ একটাতেই query-এর "Retriever" শব্দটা হুবহু আছে |
| **BM25** (sparse) | শুধু ১টা chunk | একই কারণ — exact keyword match |
| **Dense (LSA)** | ৩টা chunk | "Embedding", "Vector database" চাঙ্কগুলোও পেয়েছে — কারণ এগুলো **অর্থগতভাবে** কাছাকাছি বিষয়, যদিও query-তে সেই শব্দ নেই |
| **Hybrid** | Sparse ও Dense দুটোর স্কোর মিলিয়ে final ranking | সবচেয়ে ভারসাম্যপূর্ণ ফলাফল দেয় |

**মূল পার্থক্য চোখে পড়ার মতো:** Dense retriever "Vector database" আর "Embedding" সংক্রান্ত chunk-ও প্রাসঙ্গিক হিসেবে ধরেছে, কারণ এগুলো Retriever-এর সাথে **সম্পর্কিত concept** — যদিও কোনো শব্দ হুবহু মেলেনি। এটাই sparse আর dense-এর মূল পার্থক্য।

**একটা গুরুত্বপূর্ণ নোট:** বাস্তব প্রোডাকশন সিস্টেমে Dense retriever-এর জন্য সাধারণত `sentence-transformers` বা OpenAI-এর pretrained embedding model ব্যবহার করা হয় (অনেক বেশি ভালো semantic বোঝে), কিন্তু এই sandbox-এ Hugging Face থেকে model ডাউনলোডের সুযোগ নেই বলে আমি TF-IDF+SVD (LSA) ব্যবহার করেছি — concept একই, শুধু accuracy কম।


---
---
---


chunk_size একটু ছোট হওয়ায় বাক্য অদ্ভুতভাবে ভেঙে যাচ্ছে — ঠিক করে দিচ্ছি।সুন্দর, এখন পরিষ্কারভাবে ৫টা chunk তৈরি হচ্ছে এবং সঠিকভাবে retrieve হচ্ছে।**এই কোডে কী যোগ হলো:**

1. **`RecursiveCharacterTextSplitter`** — LangChain-এর নিজস্ব chunking টুল, নিজে হাতে split না করে এটা দিয়ে বাক্য/লাইন অনুযায়ী স্বয়ংক্রিয়ভাবে chunk করা হয়েছে (`chunk_overlap` দিয়ে পাশাপাশি chunk-এ কিছুটা তথ্য common রাখা হয়, যাতে context না হারায়)

2. **`CustomEmbeddings`** — LangChain-এর `Embeddings` ইন্টারফেস implement করা একটি ক্লাস। এটাই মূল সুবিধা: আপনি চাইলে শুধু এই ক্লাসটা বদলে `OpenAIEmbeddings` বা `HuggingFaceEmbeddings` বসিয়ে দিলেই বাকি পুরো কোড (Chroma, retriever) অপরিবর্তিত থাকবে

3. **`Chroma.from_documents()`** — vector database-এ automatically embedding তৈরি ও সংরক্ষণ করে

4. **`vectorstore.as_retriever()`** — LangChain-এর standard retriever ইন্টারফেস, যা পরে সরাসরি একটা RAG chain-এ (`RetrievalQA` বা LCEL chain) প্লাগ করা যায়

**⚠️ মনে রাখবেন:** এই sandbox-এ ইন্টারনেট restriction থাকায় real pretrained embedding (OpenAI/HuggingFace) ব্যবহার করা যায়নি — তাই accuracy কম দেখাচ্ছে। আপনার নিজের মেশিনে/সার্ভারে রান করলে কোডের উপরে দেওয়া কমেন্ট অনুযায়ী `OpenAIEmbeddings` বা `HuggingFaceEmbeddings` বসিয়ে নিলেই এটা প্রোডাকশন-রেডি RAG retriever হয়ে যাবে।


---
