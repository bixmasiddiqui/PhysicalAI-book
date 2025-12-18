"""
API Routes for Content Personalization
Endpoints: POST /api/personalize, GET /api/personalize/cache-stats
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from auth.database import get_db, User
from auth.routes import get_current_user
from .models import PersonalizeRequest, PersonalizeResponse, CacheStatsResponse
from .engine import PersonalizationEngine
from .cache_manager import CacheManager
from .transformer import ContentTransformer

router = APIRouter()

@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize_chapter(
    request: PersonalizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Personalize chapter content based on user profile

    **Authentication Required**: JWT bearer token

    **Rate Limit**: 10 requests per minute per user

    **Returns**: Personalized markdown content with metadata
    """
    try:
        # Initialize engine
        engine = PersonalizationEngine(db)

        # Get user's onboarding profile
        onboarding = current_user.onboarding or {}

        if not onboarding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile incomplete. Please complete onboarding first."
            )

        # Personalize content
        personalized_content, metadata = await engine.personalize(
            user_id=current_user.id,
            chapter_id=request.chapter_id,
            onboarding=onboarding
        )

        # Determine if cached
        cached = metadata.get("llm_provider") is None and not metadata.get("fallback_used")

        # Determine transformations
        transformer = ContentTransformer()
        transformations = transformer.determine_transformations(onboarding)

        # Build response
        variant_id = f"{request.chapter_id}-user-{current_user.id}-v1-{metadata['profile_hash'][:6]}"

        response = PersonalizeResponse(
            original_chapter_id=request.chapter_id,
            personalized_variant_id=variant_id,
            content=personalized_content,
            applied_transformations=transformations,
            cached=cached,
            metadata=metadata
        )

        # Add warning if fallback was used
        if metadata.get("fallback_used"):
            response.warning = "Personalization temporarily unavailable. Showing original content."

        return response

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalization failed: {str(e)}"
        )

@router.get("/personalize/cache-stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cache statistics for current user

    **Authentication Required**: JWT bearer token

    **Returns**: Cache metrics (total cached, hit rate, chapters)
    """
    try:
        cache_manager = CacheManager(db)
        stats = cache_manager.get_stats(current_user.id)

        return CacheStatsResponse(**stats)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )

@router.get("/personalize/health")
async def personalize_health():
    """Health check for personalization module"""
    return {
        "status": "ok",
        "module": "personalization",
        "endpoints": {
            "personalize": "POST /api/personalize",
            "cache_stats": "GET /api/personalize/cache-stats"
        }
    }
