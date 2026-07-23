# 📄 PDF Question-Answering System (Free & Local)

Ask questions about your PDF files and get answers with cited sources — by typing or by voice. Everything runs on your own machine and is free; only the spoken-answer feature needs an internet connection.

Built with Ollama + HuggingFace + Chroma.

## Features

- **Upload multiple PDFs** — they're merged into one searchable knowledge base.
- **Ask by typing or speaking** — press the mic, speak your question, and it fills in automatically.
- **Answers with sources** — see exactly which parts of your PDFs the answer came from.
- **Hear the answer read aloud** — optional text-to-speech in a male or female voice (auto-detects English or Bengali).
- **Runs locally and free** — no API keys, your documents never leave your computer.

## What you need first

1. **Python 3.14** (or a compatible 3.x).
2. **[Ollama](https://ollama.com)** installed and running.
3. **At least one language model** downloaded, for example:

   ```bash
   ollama pull llama3
   ```

   The app also lists `phi3` and `mistral` — pull whichever you want to use.



## Clone Repo
```
git clone github_path
```

## Go to repo
```
cd ~/LangChain-Learning/projects/_7_mini_rag_pdf_reader_qa
```



## Create Virtualenv
```
virtualenv -p python3.14 venv
```
## Activate vittualenv

__Linux__
```
source venv/bin/activate
```

__Windows__

```
venv\Scripts\activate
```

## Setup

```bash
# 1. Install the dependencies
pip install -r requirements.txt

# 2. Start the app
streamlit run app.py
```

The app opens in your browser.

## How to use it

1. **Upload** one or more PDF files.
2. Wait for the "PDF(s) merged" confirmation (first load embeds the documents and takes a moment).
3. **Ask a question** — type it and press **Enter** (or click **Find answer**), or use the 🎤 mic button to speak it.
4. Read the answer, expand **"View the sources"** to see where it came from, and optionally listen to it read aloud.

Use the **⚙️ Settings** sidebar to switch models, tune how much text is retrieved, and turn voice on or off.

## Notes

- The first question on a new set of PDFs is slower because the documents are being processed; later questions are faster.
- Answers are drawn **only** from your uploaded PDFs — if the answer isn't in them, the app will say it doesn't know.
- Spoken answers (text-to-speech) require an internet connection; everything else works offline.
