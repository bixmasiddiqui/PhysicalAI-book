"""
Pydantic models for personalization requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PersonalizeRequest(BaseModel):
    chapter_id: str = Field(..., pattern=r'^chapter-\d{2}$', description="Chapter identifier (e.g., chapter-01)")

class PersonalizeResponse(BaseModel):
    original_chapter_id: str
    personalized_variant_id: str
    content: str
    applied_transformations: List[str]
    cached: bool
    metadata: Dict[str, Any]
    warning: Optional[str] = None

class CacheStatsResponse(BaseModel):
    total_cached: int
    hit_rate: float
    chapters_cached: List[str]
    total_size_kb: int
    last_updated: Optional[str]
