import streamlit as st
import tempfile
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# ===== পেজ কনফিগারেশন =====
st.set_page_config(page_title="PDF Q&A (RAG)", page_icon="📄", layout="centered")
st.title("📄 PDF প্রশ্ন-উত্তর সিস্টেম (ফ্রি ও লোকাল)")
st.caption("Ollama + HuggingFace + Chroma ব্যবহার করে তৈরি")

# ===== Session State (একবার লোড হলে বারবার লোড না করার জন্য) =====
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

# ===== সাইডবার: মডেল সিলেকশন =====
with st.sidebar:
    st.header("⚙️ সেটিংস")
    model_name = st.selectbox(
        "Ollama মডেল নির্বাচন করুন",
        ["llama3", "phi3", "mistral"],
        help="আগে থেকে 'ollama pull <model>' দিয়ে ডাউনলোড করা থাকতে হবে"
    )
    chunk_size = st.slider("Chunk Size", 500, 2000, 1000, step=100)
    k_value = st.slider("কয়টা সোর্স খুঁজবে (k)", 1, 5, 3)

# ===== ফাইল আপলোড =====
uploaded_file = st.file_uploader("📤 একটি PDF ফাইল আপলোড করুন", type="pdf")

# ===== PDF প্রসেস করার ফাংশন =====
def process_pdf(file, chunk_size, k_value, model_name):
    with st.spinner("PDF প্রসেস হচ্ছে... একটু সময় লাগবে ⏳"):
        # টেম্প ফাইলে সেভ করা
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # ১. PDF লোড
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # ২. Chunk ভাগ করা
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=150
        )
        chunks = splitter.split_documents(documents)

        # ৩. Embedding
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # ৪. Chroma vectorstore (in-memory, প্রতিটি নতুন ফাইলের জন্য আলাদা)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k_value})

        # ৫. LLM
        llm = ChatOllama(model=model_name)

        # ৬. RAG প্রম্পট (retrieved context থেকে উত্তর দিতে বলা হচ্ছে)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "আপনি একজন সহায়ক অ্যাসিস্ট্যান্ট। শুধুমাত্র নিচের context ব্যবহার করে "
             "প্রশ্নের উত্তর দিন। উত্তর context-এ না থাকলে বলুন যে আপনি জানেন না। "
             "প্রশ্ন যে ভাষায় করা হয়েছে সেই ভাষাতেই উত্তর দিন।\n\n"
             "Context:\n{context}"),
            ("human", "{input}"),
        ])

        # ৭. QA Chain (RetrievalQA-এর আধুনিক প্রতিস্থাপন)
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

        os.unlink(tmp_path)  # টেম্প ফাইল মুছে ফেলা
        return qa_chain, len(chunks)

# ===== ফাইল প্রসেসিং লজিক =====
if uploaded_file is not None:
    if st.session_state.processed_file != uploaded_file.name:
        qa_chain, num_chunks = process_pdf(uploaded_file, chunk_size, k_value, model_name)
        st.session_state.qa_chain = qa_chain
        st.session_state.processed_file = uploaded_file.name
        st.success(f"✅ '{uploaded_file.name}' প্রসেস সম্পন্ন! ({num_chunks} টি chunk তৈরি হয়েছে)")
    else:
        st.info(f"📌 '{uploaded_file.name}' ইতিমধ্যে লোড করা আছে")

# ===== প্রশ্ন করার সেকশন =====
if st.session_state.qa_chain is not None:
    st.divider()
    query = st.text_input("❓ আপনার প্রশ্ন লিখুন:")

    if st.button("উত্তর খুঁজুন 🔍") and query:
        with st.spinner("উত্তর তৈরি হচ্ছে..."):
            result = st.session_state.qa_chain.invoke({"input": query})

        st.markdown("### 📌 উত্তর")
        st.write(result["answer"])

        with st.expander("📄 কোন অংশ থেকে উত্তর এসেছে (সোর্স) দেখুন"):
            for i, doc in enumerate(result["context"], 1):
                st.markdown(f"**সোর্স {i}:**")
                st.text(doc.page_content[:300] + "...")
else:
    st.info("👆 প্রথমে একটি PDF ফাইল আপলোড করুন")
