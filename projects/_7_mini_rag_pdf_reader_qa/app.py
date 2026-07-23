import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import re
from io import BytesIO

from streamlit_mic_recorder import speech_to_text
import edge_tts

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
# vectorstore is expensive (embeds the PDF) -> rebuilt only when the file or
# chunk_size changes. qa_chain is cheap -> rebuilt when the model or k changes.
for _key in ("vectorstore", "qa_chain", "processed_file",
             "chunk_used", "model_used", "k_used", "num_chunks"):
    st.session_state.setdefault(_key, None)

# ===== Sidebar: model selection =====
with st.sidebar:
    st.header("⚙️ Settings")
    model_name = st.selectbox(
        "Select Ollama model",
        # ["qwen3.5:4b","gemma3:4b","llama3", "phi3", "mistral"],
        ["llama3", "phi3", "mistral"],
        help="Must be downloaded beforehand with 'ollama pull <model>'"
    )
    chunk_size = st.slider("Chunk Size", 500, 2000, 1000, step=100)
    k_value = st.slider("Number of sources to retrieve (k)", 1, 5, 3)
    st.divider()
    st.subheader("🎙️ Voice")
    voice_output = st.toggle("Read answer aloud (TTS)", value=True)
    voice_gender = st.radio("Voice", ["Female", "Male"], horizontal=True)
    st.caption("Voice output (edge-tts) requires an internet connection")


# Named edge-tts voices per language + gender
VOICES = {
    ("en", "Female"): "en-US-AriaNeural",
    ("en", "Male"): "en-US-GuyNeural",
    ("bn", "Female"): "bn-BD-NabanitaNeural",
    ("bn", "Male"): "bn-BD-PradeepNeural",
}


# ===== Text-to-Speech helper (convert answer to audio) =====
def text_to_speech(text, gender):
    # Use Bengali if Bengali characters are present, otherwise English
    lang = "bn" if re.search(r"[ঀ-৿]", text) else "en"
    voice = VOICES[(lang, gender)]
    communicate = edge_tts.Communicate(text, voice)
    buf = BytesIO()
    # stream_sync() avoids asyncio conflicts inside Streamlit's run loop
    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    buf.seek(0)
    return buf

# ===== File upload (multiple PDFs, merged into one knowledge base) =====
uploaded_files = st.file_uploader(
    "📤 Upload one or more PDF files", type="pdf", accept_multiple_files=True
)

# ===== Build the vectorstore (expensive: load + split + embed) =====
def build_vectorstore(files, chunk_size):
    with st.spinner("Processing PDF(s)... this may take a moment ⏳"):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=150
        )

        # 1 + 2. Load and split every uploaded PDF, merging their chunks so the
        # answers can draw from all documents at once.
        chunks = []
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(file.getvalue())
                tmp_path = tmp_file.name

            documents = PyPDFLoader(tmp_path).load()
            # Tag each chunk with its source filename (shown in the sources list)
            for doc in documents:
                doc.metadata["source"] = file.name
            chunks.extend(splitter.split_documents(documents))

            os.unlink(tmp_path)  # Delete the temp file

        # 3. Embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # 4. Chroma vectorstore (in-memory, holds chunks from all PDFs)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        return vectorstore, len(chunks)


# ===== Build the QA chain (cheap: wires the retriever + selected LLM) =====
def build_qa_chain(vectorstore, k_value, model_name):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k_value})

    # LLM — this is where the selected Ollama model takes effect.
    # num_predict raises the generation cap so answers aren't cut short;
    # num_ctx widens the context window so more retrieved text fits.
    llm = ChatOllama(model=model_name, num_predict=1024, num_ctx=8192)

    # RAG prompt (answer only from the retrieved context)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a helpful assistant. Answer the question using only the "
         "context below.\n\n"
         "Write a thorough, complete answer:\n"
         "- Explain fully and include all relevant details, facts, and figures "
         "found in the context.\n"
         "- Use as much length as the question needs — do not be terse or "
         "one-line unless the question truly calls for a short factual answer.\n"
         "- Use paragraphs or bullet points / numbered steps where that makes "
         "the answer clearer.\n"
         "- If the answer is not in the context, say that you don't know.\n"
         "- Answer in the same language the question was asked in.\n\n"
         "Context:\n{context}"),
        ("human", "{input}"),
    ])

    # QA Chain (modern replacement for RetrievalQA)
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, combine_docs_chain)


# ===== File processing logic =====
if uploaded_files:
    # Signature of the current selection: (name, size) per file, order-independent
    file_sig = sorted((f.name, f.size) for f in uploaded_files)

    # (Re)embed only when the set of files or the chunk size changes
    if (st.session_state.processed_file != file_sig
            or st.session_state.chunk_used != chunk_size):
        vectorstore, num_chunks = build_vectorstore(uploaded_files, chunk_size)
        st.session_state.vectorstore = vectorstore
        st.session_state.processed_file = file_sig
        st.session_state.chunk_used = chunk_size
        st.session_state.num_chunks = num_chunks
        st.session_state.model_used = None  # force chain rebuild below
        names = ", ".join(f"'{f.name}'" for f in uploaded_files)
        st.success(
            f"✅ {len(uploaded_files)} PDF(s) merged: {names} "
            f"({num_chunks} chunks created)"
        )
    else:
        st.info(f"📌 {len(uploaded_files)} PDF(s) already loaded")

    # (Re)build the chain when the model or k changes — cheap, no re-embedding
    if (st.session_state.model_used != model_name
            or st.session_state.k_used != k_value):
        st.session_state.qa_chain = build_qa_chain(
            st.session_state.vectorstore, k_value, model_name
        )
        st.session_state.model_used = model_name
        st.session_state.k_used = k_value

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
        # Fill the question box, flag an auto-run, then rerun so the answer is
        # generated on a clean pass where the "Generating answer..." spinner
        # renders reliably (instead of during the mic component's own rerun).
        st.session_state.query_text = voice_text
        st.session_state.auto_run = True
        st.rerun()

    # ---- Turn the mic button green while recording, white when stopped ----
    # The button lives inside the component's iframe, so we reach into it with
    # JS (this components.html iframe runs with same-origin access). One click
    # starts recording -> green; the next click (Stop) -> reset to white.
    components.html(
        """
        <script>
        const doc = window.parent.document;
        function bind() {
            const frame = doc.querySelector('iframe[title^="streamlit_mic_recorder"]');
            if (!frame || !frame.contentDocument) return false;
            const btn = frame.contentDocument.querySelector('button');
            if (!btn) return false;
            if (btn.dataset.greenBound) return true;
            btn.dataset.greenBound = "1";
            let recording = false;
            btn.addEventListener('click', function () {
                recording = !recording;
                btn.style.backgroundColor = recording ? '#22c55e' : '';
                btn.style.color = recording ? '#ffffff' : '';
                btn.style.borderColor = recording ? '#22c55e' : '';
            });
            return true;
        }
        const iv = setInterval(function () { if (bind()) clearInterval(iv); }, 200);
        setTimeout(function () { clearInterval(iv); }, 10000);
        </script>
        """,
        height=0,
    )

    # session_state.query_text is used as the text box value, so the spoken
    # words land here and can still be edited before searching.
    query = st.text_input("Your question:", key="query_text")

    # Run when "Find answer" is clicked OR when a voice result was just captured
    # (auto_run set after Stop) — so Stop answers automatically.
    submitted = st.button("Find answer 🔍")
    auto_run = st.session_state.pop("auto_run", False)
    if (submitted or auto_run) and query:
        with st.spinner("Generating answer..."):
            result = st.session_state.qa_chain.invoke({"input": query})

        answer = result["answer"]
        st.markdown("### 📌 Answer")
        st.write(answer)

        # ---- Voice output (read the answer aloud) ----
        if voice_output and answer.strip():
            try:
                audio = text_to_speech(answer, voice_gender)
                st.audio(audio, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.warning(f"🔇 Could not generate voice output: {e}")

        with st.expander("📄 View the sources the answer came from"):
            for i, doc in enumerate(result["context"], 1):
                origin = doc.metadata.get("source", "unknown")
                st.markdown(f"**Source {i}** — 📄 `{origin}`")
                st.text(doc.page_content[:300] + "...")
else:
    st.info("👆 Upload one or more PDF files first")
