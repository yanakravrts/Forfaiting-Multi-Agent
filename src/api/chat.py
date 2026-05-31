from fastapi import FastAPI
from pydantic import BaseModel

from src.agent import ask_agent, ask_orchestrate

app = FastAPI(title="Forfaiting Assistant")


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatTurn] = []


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    history = [{"role": t.role, "content": t.content} for t in req.history]
    answer = await ask_agent(req.message, history=history)
    return ChatResponse(response=answer)


@app.post("/orchestrate", response_model=ChatResponse)
async def orchestrate(req: ChatRequest):
    answer = await ask_orchestrate(req.message)
    return ChatResponse(response=answer)