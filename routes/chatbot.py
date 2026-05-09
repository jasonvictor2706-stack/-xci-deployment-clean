from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_chat_service import get_ai_response

router = APIRouter(tags=["AI Chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/ai/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    reply = await get_ai_response(request.message)
    return ChatResponse(reply=reply)
