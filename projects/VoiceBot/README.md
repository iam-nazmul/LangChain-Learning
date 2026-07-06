# Local Voice Bot — FastAPI + LangChain + Gemma3 (Ollama)

Talk to a local LLM with your voice. Speech-to-text and text-to-speech
run in the browser (Web Speech API), so no extra audio libraries are
needed on the backend. FastAPI + LangChain handle the reasoning by
calling Gemma3 through a local Ollama server.

## 1. Install & run Ollama with Gemma3

```bash
# install Ollama: https://ollama.com/download
ollama pull gemma3
ollama serve      # usually starts automatically after install
```

## 2. Install Python dependencies

```bash
cd voicebot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

## 4. Open the app

Go to `http://localhost:8000` in **Chrome** (best Web Speech API
support). Click the mic button, speak, and the bot will reply out
loud.

## Notes / next steps

- **Multi-turn memory** is already wired up per browser session
  (in-memory dict — resets on server restart). Swap `sessions` for
  Redis/SQLite if you need persistence across restarts or users.
- **Model swap**: change `model="gemma3"` in `main.py` to any other
  Ollama model tag (e.g. `gemma3:12b`, `llama3.1`) — just `ollama pull`
  it first.
- **Server-side STT/TTS**: if you need it to work outside Chrome, or
  want offline voice (no browser API), swap the frontend calls for
  `faster-whisper` (STT) and `edge-tts`/`piper` (TTS) on the backend
  instead — happy to wire that up if you want it.
- **Streaming responses**: for lower latency, switch `/chat` to a
  streaming endpoint using `chain.astream(...)` and read chunks on
  the frontend as they arrive.
