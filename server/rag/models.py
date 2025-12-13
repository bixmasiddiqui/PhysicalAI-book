"""
Pydantic models for RAG chatbot
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User's question or message")
    chapter_id: Optional[str] = Field(None, description="Specific chapter to query")
    selected_text: Optional[str] = Field(None, description="Selected text for context")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is ROS?",
                "chapter_id": "chapter-01",
                "selected_text": None
            }
        }

class Source(BaseModel):
    """Source document model"""
    text: str
    score: float
    chapter: Optional[str] = None
    chunk_id: Optional[int] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    sources: List[Source]
    conversation_id: Optional[int] = None
    metadata: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "ROS (Robot Operating System) is a flexible framework...",
                "sources": [
                    {
                        "text": "ROS is a framework for robot software development...",
                        "score": 0.92,
                        "chapter": "chapter-01",
                        "chunk_id": 3
                    }
                ],
                "conversation_id": 123,
                "metadata": {
                    "processing_time_ms": 850,
                    "llm_provider": "claude",
                    "tokens_used": 320
                }
            }
        }

class EmbedRequest(BaseModel):
    """Request to embed documents"""
    docs_path: str = Field(default="../docs", description="Path to docs directory")
    force_reindex: bool = Field(default=False, description="Force reindexing even if already embedded")

class EmbedResponse(BaseModel):
    """Embed response"""
    status: str
    num_documents: int
    num_chunks: int
    processing_time_s: float
