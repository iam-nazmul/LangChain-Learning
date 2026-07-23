# CLI Chatbot

A command-line chatbot powered by LangChain and the gemma3:4b LLM running locally via Ollama.

## Stack

- **LLM**: gemma3:4b (local, via Ollama)
- **Framework**: LangChain (`langchain`, `langchain_ollama`)
- **Language**: Python 3

## Project Structure

- `chatbot.py` — main CLI chatbot with conversation history loop
- `requirements.txt` — Python dependencies

## Setup

```bash
pip install -r requirements.txt
ollama pull gemma3:4b
```

## Usage

```bash
python chatbot.py
```

Type `exit` or `quit` to stop the session.

## Notes

- Conversation history is maintained for the full session (passed to the model on every turn).
- No API keys required — runs entirely on-device via Ollama.

## Skills

### Run the chatbot
```bash
python chatbot.py
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Pull or update the model
```bash
ollama pull gemma3:4b
```

### Check Ollama is running
```bash
ollama list
```

### Switch to a different model
In `chatbot.py`, change the `model` parameter in `ChatOllama(model="gemma3:4b")` to any model available in your Ollama instance (e.g., `llama3.2`, `mistral`, `phi3`).

### Change the system prompt
In `chatbot.py`, edit the `SystemMessage` content in the `history` list to customize the assistant's behavior.

### Clear conversation history mid-session
Conversation history resets each time `chatbot.py` is launched. To add an in-session `/clear` command, handle it in the input loop before appending to `history`.

# userEmail
The user's email address is nazmul@glascutr.com.

# currentDate
Today's date is 2026-06-25.
