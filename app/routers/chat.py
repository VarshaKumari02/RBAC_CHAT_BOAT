from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth_dependency import get_current_user
from app.models.users import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.controllers import chat_controller

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chatbot"],
)

@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with the RAG-enabled chatbot helper",
)
def chat_with_bot(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the RAG chatbot helper:
    - Extracts context (bookings, profile, wallet) using keyword matching.
    - Prompts the Groq LLM with the context to generate a friendly and accurate answer.
    """
    return chat_controller.handle_chat(payload.message, current_user, db)
