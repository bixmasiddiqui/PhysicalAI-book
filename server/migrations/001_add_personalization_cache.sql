-- Migration: Add personalization_cache table
-- Created: 2025-12-12
-- Feature: Content Personalization Engine

-- Add personalization_cache table
CREATE TABLE IF NOT EXISTS personalization_cache (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(50) NOT NULL,
    profile_hash VARCHAR(64) NOT NULL,
    personalized_content TEXT NOT NULL,
    applied_transformations TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1,

    CONSTRAINT unique_cache_entry UNIQUE(user_id, chapter_id, profile_hash)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_cache_user ON personalization_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_cache_chapter ON personalization_cache(chapter_id);
CREATE INDEX IF NOT EXISTS idx_cache_profile_hash ON personalization_cache(profile_hash);
CREATE INDEX IF NOT EXISTS idx_cache_created ON personalization_cache(created_at DESC);

-- Optional: Personalization analytics/logging table
CREATE TABLE IF NOT EXISTS personalization_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    chapter_id VARCHAR(50) NOT NULL,
    transformation_type VARCHAR(100),
    response_time_ms INTEGER,
    cached BOOLEAN DEFAULT FALSE,
    llm_provider VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_log_user ON personalization_log(user_id);
CREATE INDEX IF NOT EXISTS idx_log_chapter ON personalization_log(chapter_id);
CREATE INDEX IF NOT EXISTS idx_log_created ON personalization_log(created_at DESC);
