import streamlit as st
import tempfile
import os
import re
from io import BytesIO

from streamlit_mic_recorder import speech_to_text
from gtts import gTTS

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# ===== Page configuration =====
st.set_page_config(page_title="PDF Q&A (RAG)", page_icon="📄", layout="centered")
st.title("📄 PDF Question-Answering System (Free & Local)")
st.caption("Built with Ollama + HuggingFace + Chroma")

# ===== Session State (avoid reloading on every rerun) =====
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

# ===== Sidebar: model selection =====
with st.sidebar:
    st.header("⚙️ Settings")
    model_name = st.selectbox(
        "Select Ollama model",
        ["llama3", "phi3", "mistral"],
        help="Must be downloaded beforehand with 'ollama pull <model>'"
    )
    chunk_size = st.slider("Chunk Size", 500, 2000, 1000, step=100)
    k_value = st.slider("Number of sources to retrieve (k)", 1, 5, 3)
    st.divider()
    st.subheader("🎙️ Voice")
    voice_output = st.toggle("Read answer aloud (TTS)", value=True)
    st.caption("Voice output (gTTS) requires an internet connection")


# ===== Text-to-Speech helper (convert answer to audio) =====
def text_to_speech(text):
    # Use Bengali if Bengali characters are present, otherwise English
    lang = "bn" if re.search(r"[ঀ-৿]", text) else "en"
    tts = gTTS(text=text, lang=lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

# ===== File upload =====
uploaded_file = st.file_uploader("📤 Upload a PDF file", type="pdf")

# ===== PDF processing function =====
def process_pdf(file, chunk_size, k_value, model_name):
    with st.spinner("Processing PDF... this may take a moment ⏳"):
        # Save to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # 1. Load the PDF
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()

        # 2. Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=150
        )
        chunks = splitter.split_documents(documents)

        # 3. Embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 4. Chroma vectorstore (in-memory, separate for each new file)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": k_value})

        # 5. LLM
        llm = ChatOllama(model=model_name)

        # 6. RAG prompt (answer only from the retrieved context)
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful assistant. Answer the question using only the "
             "context below. If the answer is not in the context, say that you "
             "don't know. Answer in the same language the question was asked in.\n\n"
             "Context:\n{context}"),
            ("human", "{input}"),
        ])

        # 7. QA Chain (modern replacement for RetrievalQA)
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

        os.unlink(tmp_path)  # Delete the temp file
        return qa_chain, len(chunks)

# ===== File processing logic =====
if uploaded_file is not None:
    if st.session_state.processed_file != uploaded_file.name:
        qa_chain, num_chunks = process_pdf(uploaded_file, chunk_size, k_value, model_name)
        st.session_state.qa_chain = qa_chain
        st.session_state.processed_file = uploaded_file.name
        st.success(f"✅ '{uploaded_file.name}' processed! ({num_chunks} chunks created)")
    else:
        st.info(f"📌 '{uploaded_file.name}' is already loaded")

# ===== Question section =====
if st.session_state.qa_chain is not None:
    st.divider()
    st.markdown("#### ❓ Ask a question (type or use the mic)")

    # ---- Voice input (spoken question → text) ----
    voice_text = speech_to_text(
        language="en-US",
        start_prompt="🎤 Speak",
        stop_prompt="⏹️ Stop",
        just_once=True,
        use_container_width=True,
        key="stt",
    )
    if voice_text:
        st.session_state.query_text = voice_text

    # session_state.query_text is used as the text box value, so the spoken
    # words land here and can still be edited before searching.
    query = st.text_input("Your question:", key="query_text")

    if st.button("Find answer 🔍") and query:
        with st.spinner("Generating answer..."):
            result = st.session_state.qa_chain.invoke({"input": query})

        answer = result["answer"]
        st.markdown("### 📌 Answer")
        st.write(answer)

        # ---- Voice output (read the answer aloud) ----
        if voice_output and answer.strip():
            try:
                audio = text_to_speech(answer)
                st.audio(audio, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.warning(f"🔇 Could not generate voice output: {e}")

        with st.expander("📄 View the sources the answer came from"):
            for i, doc in enumerate(result["context"], 1):
                st.markdown(f"**Source {i}:**")
                st.text(doc.page_content[:300] + "...")
else:
    st.info("👆 Upload a PDF file first")
