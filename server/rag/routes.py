"""
RAG Chatbot API Routes
Integrated with auth, personalization, and translation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
from pathlib import Path

from auth.database import get_db, User, ChatHistory
from auth.routes import get_current_user
from .models import ChatRequest, ChatResponse, EmbedRequest, EmbedResponse

router = APIRouter()

# Note: Full RAG implementation requires Qdrant setup
# This is a stub that integrates with existing auth system
# For full implementation, see rag/api/main.py

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI assistant about Physical AI concepts

    **Features:**
    - Context-aware responses
    - Chapter-specific queries
    - Selected text support
    - Citation sources

    **Authentication Required**: JWT bearer token
    """
    try:
        # TODO: Implement RAG query logic
        # For now, return stub response
        response_text = f"AI response to: {request.message}"

        # Save to chat history
        chat_entry = ChatHistory(
            user_id=current_user.id,
            message=request.message,
            response=response_text,
            chapter_id=request.chapter_id
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)

        return ChatResponse(
            answer=response_text,
            sources=[],
            conversation_id=chat_entry.id,
            metadata={
                "processing_time_ms": 100,
                "llm_provider": "stub",
                "tokens_used": 0
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@router.get("/chat/history")
async def get_chat_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for authenticated user"""
    try:
        history = db.query(ChatHistory).filter(
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

        return {
            "user_id": current_user.id,
            "history": [
                {
                    "id": entry.id,
                    "message": entry.message,
                    "response": entry.response,
                    "chapter_id": entry.chapter_id,
                    "timestamp": entry.created_at.isoformat()
                }
                for entry in history
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@router.get("/rag/health")
async def rag_health():
    """Health check for RAG module"""
    return {
        "status": "ok",
        "module": "rag",
        "endpoints": {
            "chat": "POST /api/rag/chat",
            "history": "GET /api/rag/chat/history"
        },
        "note": "Full RAG implementation pending Qdrant setup"
    }
