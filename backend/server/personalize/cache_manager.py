"""
Cache Manager for personalized content
Handles database operations for PersonalizationCache
"""

from sqlalchemy.orm import Session
from auth.database import PersonalizationCache, PersonalizationLog
from typing import Optional, List
import hashlib
import json
from datetime import datetime

class CacheManager:
    """Manages personalization cache operations"""

    def __init__(self, db: Session):
        self.db = db

    def compute_profile_hash(self, onboarding: dict) -> str:
        """Compute MD5 hash of user profile for cache key"""
        # Sort keys for consistent hashing
        sorted_json = json.dumps(onboarding, sort_keys=True)
        return hashlib.md5(sorted_json.encode()).hexdigest()

    def get_cached(self, user_id: int, chapter_id: str, profile_hash: str) -> Optional[PersonalizationCache]:
        """Retrieve cached personalized content"""
        return self.db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == user_id,
            PersonalizationCache.chapter_id == chapter_id,
            PersonalizationCache.profile_hash == profile_hash
        ).first()

    def save_to_cache(
        self,
        user_id: int,
        chapter_id: str,
        profile_hash: str,
        content: str,
        transformations: List[str]
    ) -> PersonalizationCache:
        """Save personalized content to cache"""
        cache_entry = PersonalizationCache(
            user_id=user_id,
            chapter_id=chapter_id,
            profile_hash=profile_hash,
            personalized_content=content,
            applied_transformations=transformations
        )

        self.db.add(cache_entry)
        self.db.commit()
        self.db.refresh(cache_entry)

        return cache_entry

    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a user (when profile changes)"""
        self.db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == user_id
        ).delete()
        self.db.commit()

    def invalidate_chapter_cache(self, chapter_id: str):
        """Invalidate all cache entries for a chapter (when content updates)"""
        self.db.query(PersonalizationCache).filter(
            PersonalizationCache.chapter_id == chapter_id
        ).delete()
        self.db.commit()

    def log_request(
        self,
        user_id: int,
        chapter_id: str,
        transformation_type: str,
        response_time_ms: int,
        cached: bool,
        llm_provider: Optional[str] = None
    ):
        """Log personalization request for analytics"""
        log_entry = PersonalizationLog(
            user_id=user_id,
            chapter_id=chapter_id,
            transformation_type=transformation_type,
            response_time_ms=response_time_ms,
            cached=cached,
            llm_provider=llm_provider
        )

        self.db.add(log_entry)
        self.db.commit()

    def get_stats(self, user_id: int) -> dict:
        """Get cache statistics for a user"""
        cached_entries = self.db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == user_id
        ).all()

        total_logs = self.db.query(PersonalizationLog).filter(
            PersonalizationLog.user_id == user_id
        ).count()

        cached_requests = self.db.query(PersonalizationLog).filter(
            PersonalizationLog.user_id == user_id,
            PersonalizationLog.cached == True
        ).count()

        hit_rate = (cached_requests / total_logs * 100) if total_logs > 0 else 0.0

        total_size = sum(len(entry.personalized_content.encode('utf-8')) for entry in cached_entries)

        return {
            "total_cached": len(cached_entries),
            "hit_rate": round(hit_rate, 2),
            "chapters_cached": [entry.chapter_id for entry in cached_entries],
            "total_size_kb": round(total_size / 1024, 2),
            "last_updated": cached_entries[-1].created_at.isoformat() if cached_entries else None
        }
