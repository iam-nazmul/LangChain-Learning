# Text Splitters — বড় ডকুমেন্ট ছোট Chunk-এ ভাঙা

## কেন দরকার?

ধরুন আপনার কাছে ১০০ পৃষ্ঠার একটা PDF আছে। এটা নিয়ে দুইটা সমস্যা:

1. **Embedding model-এর limit** — বেশিরভাগ embedding model একবারে ৫১২ বা ৮১৯২ token-এর বেশি নিতে পারে না। পুরো ডকুমেন্ট একসাথে embed করা যায় না।
2. **Retrieval-এর precision** — পুরো ডকুমেন্টকে একটা vector বানালে সেটা খুব "generic" হয়ে যায়। User যখন specific প্রশ্ন করবে ("refund policy কী?"), তখন শুধু relevant অংশটুকু খুঁজে পাওয়া দরকার, পুরো বই না।

তাই ডকুমেন্টকে ছোট ছোট **chunk**-এ ভাঙা হয় — প্রতিটা chunk আলাদাভাবে embed হয় এবং vector store-এ যায়।

## RecursiveCharacterTextSplitter কীভাবে কাজ করে?

এটা LangChain-এর সবচেয়ে জনপ্রিয় splitter। "Recursive" নামটার কারণ — এটা একটা **separator-এর priority list** ধরে ধাপে ধাপে ভাঙার চেষ্টা করে:

```
["\n\n", "\n", " ", ""]
```

মানে:
1. প্রথমে **paragraph** (`\n\n`) দিয়ে ভাঙার চেষ্টা করে
2. Chunk এখনও বড় হলে **line** (`\n`) দিয়ে ভাঙে
3. তাও বড় হলে **word** (space) দিয়ে
4. একদম শেষ উপায় হিসেবে **character** ধরে কাটে

এই approach-এর সুবিধা: যতটা সম্ভব **semantic boundary** (paragraph, sentence) অক্ষত রাখে — মাঝপথে বাক্য কেটে ফেলে না, যদি না বাধ্য হয়।

## Code Example

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # প্রতি chunk সর্বোচ্চ ১০০০ character
    chunk_overlap=200,    # পাশাপাশি chunk-এ ২০০ character মিলবে
)

chunks = splitter.split_documents(documents)
# অথবা raw text-এর জন্য:
# chunks = splitter.split_text(long_text)

print(len(chunks))
print(chunks[0].page_content)
```

## দুইটা গুরুত্বপূর্ণ Parameter

**`chunk_size`** — একটা chunk কত বড় হবে। ছোট রাখলে retrieval precise হয় কিন্তু context কম থাকে; বড় রাখলে context বেশি কিন্তু "noise" ঢুকে যেতে পারে। সাধারণত ৫০০–১৫০০ character দিয়ে শুরু করা হয়।

**`chunk_overlap`** — পরপর দুইটা chunk-এর মধ্যে কতটুকু text repeat হবে। ধরুন একটা গুরুত্বপূর্ণ বাক্য ঠিক chunk-এর সীমানায় পড়ল — overlap না থাকলে সেটার অর্থ দুই ভাগে ভাগ হয়ে হারিয়ে যেত। Overlap থাকলে boundary-র information দুই chunk-এই থাকে। সাধারণত chunk_size-এর ১০–২০% রাখা হয়।

## একটা ছোট উদাহরণ

```
Text: "LangChain হলো একটা framework।\n\nএটা দিয়ে RAG বানানো যায়।\n\nVector store লাগে।"

chunk_size=40 হলে:
Chunk 1: "LangChain হলো একটা framework।"
Chunk 2: "এটা দিয়ে RAG বানানো যায়।"
Chunk 3: "Vector store লাগে।"
```

দেখুন — প্রতিটা paragraph অক্ষত আছে, মাঝখান থেকে কাটেনি।

## RAG Pipeline-এ এর জায়গা

```
Document Loader → Text Splitter → Embeddings → Vector Store → Retriever → LLM
                      ↑
                  আপনি এখানে
```

একটা practical টিপ: code, Markdown, বা HTML split করতে হলে `RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)` ব্যবহার করা যায় — এটা language-specific separator (যেমন `def`, `class`) ধরে ভাঙে।

পরের ধাপ (Embeddings বা Vector Store) explain করতে চাইলে বলুন!