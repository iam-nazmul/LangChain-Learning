"""
ChatAnthropic example with configuration options.

Install:
    pip install -U langchain-anthropic langchain-community beautifulsoup4
"""


# pip install -U langchain-anthropic
# export ANTHROPIC_API_KEY="your-api-key"

import anthropic
from langchain_anthropic import ChatAnthropic

from dotenv import load_dotenv
load_dotenv()


from langchain_community.document_loaders import TextLoader, BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage


model = ChatAnthropic(
    # model="claude-sonnet-4-5-20250929",
    model="claude-haiku-4-5-20251001",
    temperature=0,
    max_tokens=1024,
    # timeout=,
    max_retries=5,   # retries 429/500/529 (overloaded) errors with exponential backoff
    # base_url="...",
    # Refer to API reference for full list of parameters
)


# ---------------------------------------------------------------------------
# 1. Load a document
#    A loader returns a list[Document]; each Document has .page_content + .metadata
# ---------------------------------------------------------------------------
# loader = TextLoader("data.txt", encoding="utf-8")
# documents = loader.load()


# BSHTMLLoader parses a LOCAL html file with BeautifulSoup (pip install bs4 lxml).
# Note: it uses `open_encoding`, not `encoding`. For a remote URL use WebBaseLoader instead.
loader = BSHTMLLoader("index.html", open_encoding="utf-8")
documents = loader.load()





# ---------------------------------------------------------------------------
# 2. Split it into chunks (so a large file fits the model's context window)
# ---------------------------------------------------------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(documents)

print(f"Loaded {len(documents)} document(s), split into {len(chunks)} chunk(s).")


# ---------------------------------------------------------------------------
# 3. Feed the content to the model
#    (For a small file we pass the whole text; for large corpora you'd embed
#     the chunks into a vector store and retrieve only the relevant ones.)
# ---------------------------------------------------------------------------
context = "\n\n".join(doc.page_content for doc in documents)

messages = [
    SystemMessage(
        content="You are a helpful assistant. Answer only from the provided context."
    ),
    HumanMessage(
        content=f"Summarize the following document in 3 bullet points:\n\n{context}"
    ),
]

try:
    response = model.invoke(messages)
    print("\n--- Summary ---")
    print(response.content)


except anthropic.OverloadedError:
    # 529: Anthropic's API is temporarily overloaded. Not a bug — retry later.
    print("\nAnthropic API is overloaded (529). Please try again in a moment.")

