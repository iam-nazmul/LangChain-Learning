# Mini_RAG_PDF_Reader_QA.md — Mini RAG PDF Reader Q&A

Developer/agent guidance for this project. User-facing setup lives in [README.md](README.md).

## Architecture

```mermaid
flowchart TD
    U([User]) -->|upload PDFs| UP[st.file_uploader]
    U -->|type or speak| Q[Question form / mic]

    subgraph Ingest["build_vectorstore() — expensive, cached in session_state"]
        UP --> LOAD[PyPDFLoader]
        LOAD --> SPLIT[RecursiveCharacterTextSplitter]
        SPLIT --> EMB[HuggingFaceEmbeddings<br/>all-MiniLM-L6-v2]
        EMB --> VS[(Chroma vectorstore<br/>in-memory)]
    end

    subgraph Chain["build_qa_chain() — cheap, rebuilt on model/k change"]
        VS --> RET[retriever k=k_value]
        RET --> STUFF[create_stuff_documents_chain]
        LLM[ChatOllama<br/>local model] --> STUFF
        STUFF --> RAG[create_retrieval_chain]
    end

    Q --> RAG
    RAG -->|answer + context| ANS[st.write answer + sources]
    ANS -->|optional| TTS[edge-tts text_to_speech]
    TTS --> AUDIO[st.audio autoplay]
    STT[streamlit_mic_recorder<br/>speech_to_text] --> Q
```

## Layout

Single-file app. All logic is in [app.py](app.py); config in [.streamlit/config.toml](.streamlit/config.toml).

## Key invariants

- **Session-state caching is the core performance contract.** `vectorstore` is rebuilt only when the file signature (`(name, size)` per file) or `chunk_size` changes; `qa_chain` is rebuilt only when `model_name` or `k_value` changes. Preserve this split — do not embed on every rerun.
- **Everything runs local + free** except `edge-tts` (needs internet). Embeddings (HuggingFace), vector store (Chroma), and the LLM (Ollama) require no API keys.
- **The Ollama model must be pulled first** (`ollama pull <model>`); the selectbox only lists names.
- **Chroma is in-memory** — it does not persist across process restarts.

## Actionable notes for changes

- Adding a model: extend the `st.selectbox` list in the sidebar; ensure it is `ollama pull`-able.
- Changing retrieval quality: adjust `chunk_size`/`chunk_overlap` in `build_vectorstore` or `k` in `build_qa_chain`. Changing `chunk_size` forces a re-embed (by design).
- The question box is inside `st.form("qa_form")` so Enter submits — keep the submit button as `st.form_submit_button`, not `st.button`.
- Voice input path: `speech_to_text` → sets `query_text` + `auto_run` → `st.rerun()` → answered on the clean pass. Don't answer inside the mic component's own rerun.
- TTS language auto-detects Bengali via the `[ঀ-৿]` range, else English; extend `VOICES` to add languages.
- New deps go in [requirements.txt](requirements.txt) (unpinned, matching current style).

## Run

```bash
streamlit run app.py
```

Requires a running Ollama daemon with at least one listed model pulled.
