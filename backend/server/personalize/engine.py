"""
Personalization Engine - Main orchestrator
Coordinates cache, transformation, and chapter loading
"""

import os
import time
from pathlib import Path
from typing import Tuple, Dict, Any
from sqlalchemy.orm import Session

from .cache_manager import CacheManager
from .transformer import ContentTransformer

class PersonalizationEngine:
    """Main engine for content personalization"""

    def __init__(self, db: Session):
        self.db = db
        self.cache_manager = CacheManager(db)
        self.transformer = ContentTransformer()
        self.docs_path = Path(__file__).parent.parent.parent / "docs"

    def load_chapter(self, chapter_id: str) -> str:
        """Load original chapter content from file"""
        chapter_file = self.docs_path / f"{chapter_id}.md"

        if not chapter_file.exists():
            raise FileNotFoundError(f"Chapter {chapter_id} not found")

        with open(chapter_file, 'r', encoding='utf-8') as f:
            return f.read()

    async def personalize(
        self,
        user_id: int,
        chapter_id: str,
        onboarding: dict
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Personalize chapter content for user

        Returns: (personalized_content, metadata)
        """
        start_time = time.time()

        # Compute profile hash for cache key
        profile_hash = self.cache_manager.compute_profile_hash(onboarding)

        # Check cache first
        cached_entry = self.cache_manager.get_cached(user_id, chapter_id, profile_hash)

        if cached_entry:
            # Cache hit!
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log request
            self.cache_manager.log_request(
                user_id=user_id,
                chapter_id=chapter_id,
                transformation_type="cached",
                response_time_ms=response_time_ms,
                cached=True
            )

            metadata = {
                "processing_time_ms": response_time_ms,
                "profile_hash": profile_hash,
                "llm_provider": None,
                "fallback_used": False
            }

            return cached_entry.personalized_content, metadata

        # Cache miss - need to generate
        try:
            # Load original chapter
            original_content = self.load_chapter(chapter_id)

            # Transform using LLM
            personalized_content, transformations = await self.transformer.transform_content(
                original_content,
                onboarding
            )

            # Save to cache
            self.cache_manager.save_to_cache(
                user_id=user_id,
                chapter_id=chapter_id,
                profile_hash=profile_hash,
                content=personalized_content,
                transformations=transformations
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log request
            self.cache_manager.log_request(
                user_id=user_id,
                chapter_id=chapter_id,
                transformation_type=",".join(transformations),
                response_time_ms=response_time_ms,
                cached=False,
                llm_provider=self.transformer.llm_provider
            )

            metadata = {
                "processing_time_ms": response_time_ms,
                "profile_hash": profile_hash,
                "llm_provider": self.transformer.llm_provider,
                "fallback_used": False
            }

            return personalized_content, metadata

        except Exception as e:
            # Fallback to original content on error
            print(f"Personalization error: {str(e)}")

            original_content = self.load_chapter(chapter_id)
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log failed request
            self.cache_manager.log_request(
                user_id=user_id,
                chapter_id=chapter_id,
                transformation_type="fallback",
                response_time_ms=response_time_ms,
                cached=False
            )

            metadata = {
                "processing_time_ms": response_time_ms,
                "profile_hash": profile_hash,
                "llm_provider": None,
                "fallback_used": True,
                "fallback_reason": str(e)
            }

            return original_content, metadata
