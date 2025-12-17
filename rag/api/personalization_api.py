"""
Personalization API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

from .database import get_db, UserProfile, PersonalizationCache
from personalization.personalization_engine import PersonalizationEngine

router = APIRouter(prefix="/personalization", tags=["personalization"])

# Initialize engine
personalization_engine = PersonalizationEngine(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

class PersonalizeRequest(BaseModel):
    chapter: str
    user_id: str
    difficulty: Optional[str] = None

class UserProfileUpdate(BaseModel):
    user_id: str
    education_level: str
    programming_background: str
    math_background: str
    hardware_background: str

@router.post("/personalize-chapter")
async def personalize_chapter(request: PersonalizeRequest, db=Depends(get_db)):
    """
    Personalize a chapter for a specific user
    """
    try:
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == request.user_id
        ).first()

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found. Please complete onboarding first."
            )

        # Check cache
        cached = db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == request.user_id,
            PersonalizationCache.chapter == request.chapter,
            PersonalizationCache.difficulty_level == (request.difficulty or 'auto')
        ).first()

        if cached:
            return {
                "personalized_content": cached.personalized_content,
                "difficulty": cached.difficulty_level,
                "cached": True
            }

        # Load chapter content (simplified - in practice load from file)
        chapter_path = f"./docs/{request.chapter}.md"
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
        except:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Personalize
        user_profile_dict = {
            'education_level': user_profile.education_level,
            'programming_background': user_profile.programming_background,
            'math_background': user_profile.math_background,
            'hardware_background': user_profile.hardware_background
        }

        personalized = personalization_engine.personalize_chapter(
            chapter_content=chapter_content,
            user_profile=user_profile_dict,
            difficulty=request.difficulty
        )

        # Cache the result
        cache_entry = PersonalizationCache(
            user_id=request.user_id,
            chapter=request.chapter,
            difficulty_level=request.difficulty or 'auto',
            personalized_content=personalized
        )
        db.add(cache_entry)
        db.commit()

        return {
            "personalized_content": personalized,
            "difficulty": request.difficulty or 'auto',
            "cached": False
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-profile")
async def update_user_profile(profile: UserProfileUpdate, db=Depends(get_db)):
    """
    Update or create user profile
    """
    try:
        existing = db.query(UserProfile).filter(
            UserProfile.user_id == profile.user_id
        ).first()

        if existing:
            existing.education_level = profile.education_level
            existing.programming_background = profile.programming_background
            existing.math_background = profile.math_background
            existing.hardware_background = profile.hardware_background
        else:
            new_profile = UserProfile(
                user_id=profile.user_id,
                education_level=profile.education_level,
                programming_background=profile.programming_background,
                math_background=profile.math_background,
                hardware_background=profile.hardware_background
            )
            db.add(new_profile)

        db.commit()

        return {"status": "success", "message": "Profile updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str, db=Depends(get_db)):
    """
    Get user profile
    """
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "user_id": profile.user_id,
        "education_level": profile.education_level,
        "programming_background": profile.programming_background,
        "math_background": profile.math_background,
        "hardware_background": profile.hardware_background
    }
