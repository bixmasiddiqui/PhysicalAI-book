"""
Translation Cache Manager
Handles database operations for translation caching
"""

import hashlib
import json
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from auth.database import TranslationCache

class TranslationCacheManager:
    """Manages translation cache operations"""

    def __init__(self, db: Session):
        self.db = db

    def compute_content_hash(self, content: str) -> str:
        """
        Compute MD5 hash of content for cache invalidation

        Args:
            content: Source content string

        Returns:
            MD5 hash (32 characters hex)
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get_cached_translation(
        self,
        chapter_id: str,
        language: str,
        content_hash: str
    ) -> Optional[TranslationCache]:
        """
        Retrieve cached translation if exists

        Args:
            chapter_id: Chapter identifier
            language: Target language code
            content_hash: MD5 hash of source content

        Returns:
            TranslationCache object or None if cache miss
        """
        try:
            cached = self.db.query(TranslationCache).filter(
                TranslationCache.chapter_id == chapter_id,
                TranslationCache.language == language,
                TranslationCache.content_hash == content_hash
            ).first()

            return cached
        except Exception as e:
            print(f"Cache retrieval error: {str(e)}")
            return None

    def save_translation(
        self,
        chapter_id: str,
        language: str,
        content_hash: str,
        translated_content: str
    ) -> bool:
        """
        Save translation to cache

        Args:
            chapter_id: Chapter identifier
            language: Target language code
            content_hash: MD5 hash of source content
            translated_content: Translated markdown content

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Check if entry already exists
            existing = self.db.query(TranslationCache).filter(
                TranslationCache.chapter_id == chapter_id,
                TranslationCache.language == language,
                TranslationCache.content_hash == content_hash
            ).first()

            if existing:
                # Update existing
                existing.translated_content = translated_content
                existing.version += 1
            else:
                # Create new entry
                new_cache = TranslationCache(
                    chapter_id=chapter_id,
                    language=language,
                    content_hash=content_hash,
                    translated_content=translated_content
                )
                self.db.add(new_cache)

            self.db.commit()
            return True

        except Exception as e:
            print(f"Cache save error: {str(e)}")
            self.db.rollback()
            return False

    def invalidate_cache(self, chapter_id: str) -> int:
        """
        Invalidate all cached translations for a chapter
        Used when original chapter is updated

        Args:
            chapter_id: Chapter to invalidate

        Returns:
            Number of cache entries deleted
        """
        try:
            deleted_count = self.db.query(TranslationCache).filter(
                TranslationCache.chapter_id == chapter_id
            ).delete()

            self.db.commit()
            return deleted_count

        except Exception as e:
            print(f"Cache invalidation error: {str(e)}")
            self.db.rollback()
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache metrics
        """
        try:
            # Total cached translations
            total_cached = self.db.query(TranslationCache).count()

            # Breakdown by language
            language_stats = self.db.query(
                TranslationCache.language,
                func.count(TranslationCache.id).label('count')
            ).group_by(TranslationCache.language).all()

            languages = [
                {"language": lang, "count": count}
                for lang, count in language_stats
            ]

            # Unique chapters cached
            chapters_cached = [
                row[0] for row in self.db.query(
                    TranslationCache.chapter_id
                ).distinct().all()
            ]

            # Calculate total cache size (approximate)
            total_size = self.db.query(
                func.sum(func.length(TranslationCache.translated_content))
            ).scalar() or 0
            total_size_kb = total_size / 1024

            # Last updated timestamp
            last_entry = self.db.query(TranslationCache).order_by(
                desc(TranslationCache.updated_at)
            ).first()
            last_updated = last_entry.updated_at.isoformat() if last_entry else None

            # Calculate hit rate (simplified - based on version numbers)
            # Higher average version = more cache hits
            avg_version = self.db.query(
                func.avg(TranslationCache.version)
            ).scalar() or 1.0

            # Estimate hit rate: (avg_version - 1) / avg_version * 100
            hit_rate = ((avg_version - 1) / avg_version * 100) if avg_version > 1 else 0.0

            return {
                "total_cached": total_cached,
                "languages": languages,
                "chapters_cached": chapters_cached,
                "hit_rate": round(hit_rate, 2),
                "total_size_kb": round(total_size_kb, 2),
                "last_updated": last_updated
            }

        except Exception as e:
            print(f"Stats retrieval error: {str(e)}")
            return {
                "total_cached": 0,
                "languages": [],
                "chapters_cached": [],
                "hit_rate": 0.0,
                "total_size_kb": 0.0,
                "last_updated": None
            }
