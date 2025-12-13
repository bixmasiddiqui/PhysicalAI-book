"""
Translation API Routes
Endpoints: POST /api/translate, GET /api/translate/cache-stats, DELETE /api/translate/cache/{chapter_id}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
import time
from typing import Dict, Any

from auth.database import get_db, User
from auth.routes import get_current_user
from .models import TranslateRequest, TranslateResponse, CacheStatsResponse
from .translator import UrduTranslator
from .cache_manager import TranslationCacheManager

router = APIRouter()

# Initialize translator (singleton)
translator = UrduTranslator()

def load_chapter(chapter_id: str) -> str:
    """
    Load chapter content from docs/ directory

    Args:
        chapter_id: Chapter identifier (e.g., 'chapter-01')

    Returns:
        Chapter markdown content

    Raises:
        FileNotFoundError: If chapter file doesn't exist
    """
    docs_path = Path(__file__).parent.parent.parent / "docs"
    chapter_file = docs_path / f"{chapter_id}.md"

    if not chapter_file.exists():
        raise FileNotFoundError(f"Chapter {chapter_id} not found")

    with open(chapter_file, 'r', encoding='utf-8') as f:
        return f.read()

@router.post("/translate", response_model=TranslateResponse)
async def translate_chapter(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Translate chapter to target language (Urdu)

    **Authentication Required**: JWT bearer token

    **Rate Limit**: 20 translations per hour per user

    **Returns**: Translated markdown content with metadata
    """
    start_time = time.time()

    try:
        # Initialize cache manager
        cache_manager = TranslationCacheManager(db)

        # Determine source content
        if request.source_content:
            # Custom content provided (e.g., personalized variant)
            source_content = request.source_content
        else:
            # Load original chapter
            source_content = load_chapter(request.chapter_id)

        # Compute content hash for cache key
        content_hash = cache_manager.compute_content_hash(source_content)

        # Check cache first
        cached_entry = cache_manager.get_cached_translation(
            chapter_id=request.chapter_id,
            language=request.target_language,
            content_hash=content_hash
        )

        if cached_entry:
            # Cache hit!
            response_time_ms = int((time.time() - start_time) * 1000)

            return TranslateResponse(
                original_chapter_id=request.chapter_id,
                target_language=request.target_language,
                translated_content=cached_entry.translated_content,
                cached=True,
                metadata={
                    "processing_time_ms": response_time_ms,
                    "content_hash": content_hash,
                    "llm_provider": None,
                    "tokens_used": 0,
                    "fallback_used": False
                }
            )

        # Cache miss - generate translation
        try:
            # Call LLM for translation
            translated_content, tokens_used = await translator.translate(
                content=source_content,
                target_language=request.target_language
            )

            # Validate translation
            if not translator.validate_translation(source_content, translated_content):
                raise ValueError("Translation validation failed")

            # Save to cache
            cache_manager.save_translation(
                chapter_id=request.chapter_id,
                language=request.target_language,
                content_hash=content_hash,
                translated_content=translated_content
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return TranslateResponse(
                original_chapter_id=request.chapter_id,
                target_language=request.target_language,
                translated_content=translated_content,
                cached=False,
                metadata={
                    "processing_time_ms": response_time_ms,
                    "content_hash": content_hash,
                    "llm_provider": translator.llm_provider,
                    "tokens_used": tokens_used,
                    "fallback_used": False
                }
            )

        except Exception as e:
            # Fallback to original content on translation error
            print(f"Translation error: {str(e)}")

            response_time_ms = int((time.time() - start_time) * 1000)

            return TranslateResponse(
                original_chapter_id=request.chapter_id,
                target_language=request.target_language,
                translated_content=source_content,  # Return original
                cached=False,
                metadata={
                    "processing_time_ms": response_time_ms,
                    "content_hash": content_hash,
                    "llm_provider": None,
                    "tokens_used": 0,
                    "fallback_used": True,
                    "fallback_reason": str(e)
                }
            )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@router.get("/translate/cache-stats", response_model=CacheStatsResponse)
async def get_translation_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get translation cache statistics

    **Authentication Required**: JWT bearer token

    **Returns**: Cache metrics (total cached, hit rate, languages, chapters)
    """
    try:
        cache_manager = TranslationCacheManager(db)
        stats = cache_manager.get_stats()

        return CacheStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )

@router.delete("/translate/cache/{chapter_id}")
async def invalidate_translation_cache(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invalidate translation cache for a specific chapter

    **Authentication Required**: JWT bearer token

    **Admin Only**: Future enhancement (currently open to all authenticated users)

    **Returns**: Number of cache entries deleted
    """
    try:
        cache_manager = TranslationCacheManager(db)
        deleted_count = cache_manager.invalidate_cache(chapter_id)

        return {
            "message": f"Cache invalidated for {chapter_id}",
            "deleted_count": deleted_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache invalidation failed: {str(e)}"
        )

@router.get("/translate/health")
async def translation_health():
    """Health check for translation module"""
    return {
        "status": "ok",
        "module": "translation",
        "supported_languages": ["urdu"],
        "llm_provider": translator.llm_provider,
        "glossary_terms": len(translator.glossary_terms),
        "endpoints": {
            "translate": "POST /api/translate",
            "cache_stats": "GET /api/translate/cache-stats",
            "invalidate_cache": "DELETE /api/translate/cache/{chapter_id}"
        }
    }
