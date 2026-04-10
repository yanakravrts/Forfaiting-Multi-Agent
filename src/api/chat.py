from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import ask_agent

app = FastAPI(title="Forfaiting Assistant")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = await ask_agent(req.message)
    return ChatResponse(response=answer)