from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

app = FastAPI()
templates = Jinja2Templates(directory="templates")

model = ChatOllama(model="gemma3:4b")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a summarization assistant. Summarize the given text in exactly 3 concise lines. Do not add any extra explanation."),
    ("human", "Summarize this text:\n\n{text}"),
])


parser = StrOutputParser() 
chain = prompt | model | parser


class SummarizeRequest(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/summarize")
async def summarize(body: SummarizeRequest):
    result = chain.invoke({"text": body.text})
    return {"summary": result}
