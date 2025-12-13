"""
Pydantic models for translation API
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class TranslateRequest(BaseModel):
    """Request model for chapter translation"""
    chapter_id: str = Field(..., description="Chapter ID to translate", pattern=r'^chapter-\d{2}$')
    target_language: str = Field(default="urdu", description="Target language code")
    source_content: Optional[str] = Field(None, description="Optional custom content to translate")

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "chapter-01",
                "target_language": "urdu"
            }
        }

class TranslateResponse(BaseModel):
    """Response model for translation"""
    original_chapter_id: str
    target_language: str
    translated_content: str
    cached: bool
    metadata: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "original_chapter_id": "chapter-01",
                "target_language": "urdu",
                "translated_content": "# فزیکل AI...",
                "cached": False,
                "metadata": {
                    "processing_time_ms": 3250,
                    "content_hash": "a3c5f1b2",
                    "llm_provider": "claude",
                    "tokens_used": 4200,
                    "fallback_used": False
                }
            }
        }

class CacheStatsResponse(BaseModel):
    """Cache statistics response"""
    total_cached: int
    languages: List[Dict[str, Any]]
    chapters_cached: List[str]
    hit_rate: float
    total_size_kb: float
    last_updated: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_cached": 15,
                "languages": [{"language": "urdu", "count": 15}],
                "chapters_cached": ["chapter-01", "chapter-02"],
                "hit_rate": 78.5,
                "total_size_kb": 425.3,
                "last_updated": "2025-12-13T14:30:00Z"
            }
        }
