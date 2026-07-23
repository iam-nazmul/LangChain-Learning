# Text Summarizer

A web app that accepts long text as input and returns a concise 3-line summary using a local LLM via Ollama.

## Stack

- **LLM**: gemma3:4b (local, via Ollama)
- **Framework**: LangChain (`langchain`, `langchain_ollama`), FastAPI
- **Frontend**: Jinja2 templates, Tailwind CSS (CDN)
- **Language**: Python 3.12

## Project Structure

```
text_summarizer/
├── main.py              # FastAPI app, LangChain chain, API routes
├── templates/
│   └── index.html       # Single-page UI with textarea and summary display
├── requirements.txt
└── CLAUDE.md
```

## How It Works

1. User pastes text into the textarea and clicks **Summarize**
2. The frontend POSTs `{ "text": "..." }` to `POST /summarize`
3. FastAPI passes the text through a LangChain chain: `ChatPromptTemplate | ChatOllama | StrOutputParser`
4. The LLM returns a 3-line summary, which is displayed below the input

## API

| Method | Path        | Body                  | Response               |
|--------|-------------|-----------------------|------------------------|
| GET    | `/`         | —                     | HTML page              |
| POST   | `/summarize`| `{ "text": string }`  | `{ "summary": string }`|

## Running

Ollama must be running locally with the `gemma3:4b` model pulled:

```bash
ollama pull gemma3:4b
```

Install dependencies and start the server from the `projects/` directory:

```bash
pip install -r text_summarizer/requirements.txt
uvicorn text_summarizer.main:app --reload
```

Then open `http://localhost:8000`.

## Known Issues / Notes

- `TemplateResponse` requires `(request, "index.html")` argument order — Starlette 0.36+ changed the signature (passing name first causes `unhashable type: 'dict'` error).
- The LLM response time depends on local hardware; the button is disabled while waiting.
