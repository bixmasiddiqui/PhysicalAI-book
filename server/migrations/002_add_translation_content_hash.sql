-- Migration: Add content_hash to translation_cache table
-- Purpose: Enable cache invalidation when source content changes
-- Date: 2025-12-13

-- Add content_hash column (MD5 hash of source content)
ALTER TABLE translation_cache
ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);

-- Create composite index for faster lookups
CREATE INDEX IF NOT EXISTS idx_translation_cache_lookup
ON translation_cache(chapter_id, language, content_hash);

-- Update existing rows with placeholder hash (will be regenerated on next request)
UPDATE translation_cache
SET content_hash = MD5(translated_content)
WHERE content_hash IS NULL;

-- Make content_hash NOT NULL after backfill
ALTER TABLE translation_cache
ALTER COLUMN content_hash SET NOT NULL;

-- Add index on content_hash alone for invalidation queries
CREATE INDEX IF NOT EXISTS idx_translation_cache_hash
ON translation_cache(content_hash);
