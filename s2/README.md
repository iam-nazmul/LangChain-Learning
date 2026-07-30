

# LangChain Retrievers — বাংলায় ব্যাখ্যা

## Retriever আসলে কী?

**Retriever** হলো LangChain-এর একটি কম্পোনেন্ট, যেটা একটা টেক্সট কোয়েরি (query) নিয়ে সেই কোয়েরির সাথে সবচেয়ে প্রাসঙ্গিক (relevant) ডকুমেন্টগুলো খুঁজে বের করে দেয়। সহজ ভাষায় বললে, এটা একটা "সার্চ ইঞ্জিন"-এর মতো কাজ করে — আপনি একটা প্রশ্ন দিলেন, retriever সেই প্রশ্নের সাথে সম্পর্কিত `Document` অবজেক্টগুলোর একটা লিস্ট ফেরত দেয়।

RAG (Retrieval-Augmented Generation) সিস্টেমে retriever খুবই গুরুত্বপূর্ণ, কারণ এটাই LLM-কে আপনার নিজস্ব ডেটা (PDF, ডাটাবেস, ওয়েবসাইট ইত্যাদি) থেকে সঠিক তথ্য এনে দেয়, যাতে মডেল ভুল তথ্য (hallucination) না বানিয়ে বাস্তব ডেটার ভিত্তিতে উত্তর দিতে পারে।

## গুরুত্বপূর্ণ বৈশিষ্ট্য

- সব retriever `BaseRetriever` ক্লাস থেকে ইনহেরিট করে, যেটা `Runnable` ইন্টারফেস ইমপ্লিমেন্ট করে — মানে LCEL (LangChain Expression Language) পাইপলাইনে সহজেই ব্যবহার করা যায়।
- Retriever শুধু ডকুমেন্ট **খুঁজে দেয়**, নিজে **সংরক্ষণ** করে না — এই দিক থেকে এটা vector store থেকে বেশি general। যেকোনো vector store-কে retriever-এ রূপান্তর করা যায়।

## প্রধান ধরনের Retriever

1. **Vector Store-Based Retriever** — সবচেয়ে বেশি ব্যবহৃত। Chroma, Pinecone, FAISS-এর মতো vector database থেকে embedding মিলিয়ে ডকুমেন্ট খুঁজে বের করে।
2. **Wikipedia Retriever** — সরাসরি Wikipedia API থেকে তথ্য আনে।
3. **BM25 / TF-IDF Retriever** — keyword-based সার্চ, embedding ছাড়াই।
4. **Custom Retriever** — `BaseRetriever` সাবক্লাস করে নিজের লজিক দিয়ে বানানো যায়।

## উদাহরণ ১: Vector Store থেকে Retriever বানানো (সবচেয়ে সাধারণ পদ্ধতি)

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# কিছু নমুনা ডকুমেন্ট
docs = [
    Document(page_content="ঢাকা বাংলাদেশের রাজধানী।"),
    Document(page_content="পদ্মা নদী বাংলাদেশের একটি বড় নদী।"),
    Document(page_content="বাংলাদেশের জাতীয় ফুল শাপলা।"),
]

# Embedding মডেল দিয়ে vector store তৈরি
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(docs, embeddings)

# vector store কে retriever-এ রূপান্তর
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# কোয়েরি দিয়ে প্রাসঙ্গিক ডকুমেন্ট খোঁজা
results = retriever.invoke("বাংলাদেশের রাজধানী কী?")
for r in results:
    print(r.page_content)
```

## উদাহরণ ২: নিজের Custom Retriever বানানো

```python
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class SimpleRetriever(BaseRetriever):
    docs: list[Document]
    k: int = 3

    def _get_relevant_documents(self, query: str) -> list[Document]:
        """খুব সাধারণভাবে প্রথম k টা ডকুমেন্ট ফেরত দিচ্ছে"""
        return self.docs[:self.k]

    async def _aget_relevant_documents(self, query: str) -> list[Document]:
        """asynchronous ভার্সন (ঐচ্ছিক)"""
        return self.docs[:self.k]

# ব্যবহার
my_docs = [
    Document(page_content="প্রথম ডকুমেন্ট"),
    Document(page_content="দ্বিতীয় ডকুমেন্ট"),
]
retriever = SimpleRetriever(docs=my_docs, k=1)
result = retriever.invoke("যেকোনো কোয়েরি")
print(result)
```

## উদাহরণ ৩: LCEL চেইনে Retriever ব্যবহার (RAG-এর মূল প্যাটার্ন)

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_anthropic import ChatAnthropic

prompt = ChatPromptTemplate.from_template(
    "নিচের তথ্যের ভিত্তিতে প্রশ্নের উত্তর দাও:\n{context}\n\nপ্রশ্ন: {question}"
)
llm = ChatAnthropic(model="claude-sonnet-4-6")

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("বাংলাদেশের রাজধানী কী?")
print(answer)
```

**সংক্ষেপে**: Retriever হলো এমন একটা ব্রিজ, যেটা আপনার নিজের ডেটাকে LLM-এর সাথে সংযুক্ত করে দেয় — যাতে মডেল শুধু নিজের প্রশিক্ষণের জ্ঞান নয়, বরং আপনার দেওয়া প্রকৃত ডকুমেন্টের ভিত্তিতে সঠিক ও প্রাসঙ্গিক উত্তর দিতে পারে।
