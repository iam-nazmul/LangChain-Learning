from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

app = FastAPI(title="Voice Bot")

# Make sure `ollama pull gemma3` has been run and the ollama server is running.
llm = ChatOllama(model="gemma3", temperature=0.7)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful, concise voice assistant. Keep replies "
#                "short (1-3 sentences) and conversational, since they will "
#                "be read aloud by text-to-speech."),
#     MessagesPlaceholder("history"),
#     ("human", "{input}"),
# ])
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful, concise voice assistant. Keep replies "
               "short and conversational, since they will "
               "be read aloud by text-to-speech."),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

chain = prompt | llm

# In-memory chat history per session (fine for local/single-user use;
# swap for Redis/DB if you need multi-user persistence).
sessions: dict[str, list] = {}


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    history = sessions.setdefault(req.session_id, [])
    result = chain.invoke({"history": history, "input": req.message})

    history.append(HumanMessage(content=req.message))
    history.append(AIMessage(content=result.content))
    sessions[req.session_id] = history[-20:]  # cap history length

    return ChatResponse(reply=result.content)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the mic/chat UI at "/"
app.mount("/", StaticFiles(directory="static", html=True), name="static")
