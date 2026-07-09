from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_ollama import ChatOllama

# 1. লোড ও স্প্লিট
docs = WebBaseLoader("https://www.glascutr.com/").load()
splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

# 2. embed ও store
vectorstore = Chroma.from_documents(splits, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 3. RAG চেইন
prompt = ChatPromptTemplate.from_template(
    "শুধু নিচের context ব্যবহার করে উত্তর দাও:\n\n{context}\n\nপ্রশ্ন: {question}"
)
# model = ChatOpenAI(model="gpt-4o-mini")
model = ChatOllama(model="gemma3:4b", temperature=0.1)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | model | StrOutputParser()
)
print(rag_chain.invoke("মূল বক্তব্য কী?"))