# Data Model: Content Personalization Engine

**Feature**: Content Personalization
**Date**: 2025-12-12
**Related**: [plan.md](./plan.md), [spec.md](./spec.md)

## Overview

Data model for storing personalized chapter content with caching for performance. Uses composite key (user_id + chapter_id + profile_hash) to enable cache sharing between users with identical profiles while supporting profile updates.

## Entities

### PersonalizationCache (NEW)

**Purpose**: Store personalized chapter content to avoid re-generating identical transformations

**Table Name**: `personalization_cache`

**Schema**:

```sql
CREATE TABLE personalization_cache (
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

CREATE INDEX idx_cache_user ON personalization_cache(user_id);
CREATE INDEX idx_cache_chapter ON personalization_cache(chapter_id);
CREATE INDEX idx_cache_profile_hash ON personalization_cache(profile_hash);
CREATE INDEX idx_cache_created ON personalization_cache(created_at DESC);
```

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id) | Owner of personalized content |
| chapter_id | VARCHAR(50) | NOT NULL | Chapter identifier (e.g., "chapter-01") |
| profile_hash | VARCHAR(64) | NOT NULL | MD5 hash of user's onboarding JSON |
| personalized_content | TEXT | NOT NULL | Transformed markdown content |
| applied_transformations | TEXT[] | DEFAULT '{}' | List of transformations applied (e.g., ["beginner-simplify", "jetson-hardware"]) |
| created_at | TIMESTAMP | DEFAULT NOW() | When content was generated |
| version | INTEGER | DEFAULT 1 | Cache version for invalidation |

**Relationships**:
- belongs_to: User (user_id → users.id)
- Cache is deleted when user is deleted (CASCADE)

**Indexes**:
- PRIMARY: id (auto)
- UNIQUE: (user_id, chapter_id, profile_hash) - ensures one cache entry per combination
- INDEX: user_id - fast lookup of all user's cached chapters
- INDEX: chapter_id - analytics (how many personalizations per chapter)
- INDEX: profile_hash - enables cache sharing across users
- INDEX: created_at DESC - for cache cleanup/eviction policies

**Cache Key Algorithm**:

```python
import hashlib
import json

def generate_cache_key(user_id: int, chapter_id: str, onboarding: dict) -> tuple:
    """Generate composite cache key"""
    # Sort onboarding JSON to ensure consistent hashing
    sorted_json = json.dumps(onboarding, sort_keys=True)
    profile_hash = hashlib.md5(sorted_json.encode()).hexdigest()

    return (user_id, chapter_id, profile_hash)
```

**Cache Invalidation Rules**:

1. **User Profile Update**: When `user.onboarding` changes, profile_hash changes → new cache entry created
2. **Chapter Content Update**: When original chapter modified, increment `version` in all cache entries for that chapter (or delete)
3. **Manual Clear**: Admin can delete all cache entries for testing
4. **TTL (Optional)**: Delete entries older than 30 days to save storage

**Query Patterns**:

```sql
-- Lookup cached content
SELECT personalized_content, created_at
FROM personalization_cache
WHERE user_id = $1 AND chapter_id = $2 AND profile_hash = $3
LIMIT 1;

-- Invalidate user's cache on profile update
DELETE FROM personalization_cache
WHERE user_id = $1;

-- Invalidate chapter's cache on content update
DELETE FROM personalization_cache
WHERE chapter_id = $1;

-- Get cache statistics
SELECT
    COUNT(*) as total_entries,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT chapter_id) as unique_chapters,
    AVG(LENGTH(personalized_content)) as avg_content_size
FROM personalization_cache;
```

---

### User (EXISTING - from Step C)

**Table Name**: `users`

**Relevant Fields** (used for personalization):

```sql
-- Existing schema (no changes needed)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    onboarding JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Onboarding JSON Structure** (source of personalization parameters):

```json
{
    "role": "Student|Professional|Researcher|Instructor",
    "programming_experience": "Beginner|Intermediate|Advanced",
    "robotics_experience": "None|Simulation-only|Hardware",
    "preferred_language": "English|Urdu|Other",
    "hardware_availability": "RTX Workstation|Cloud|Jetson Kit|None"
}
```

**Access Pattern**:

```python
# Read user profile for personalization
user = db.query(User).filter(User.id == user_id).first()
onboarding = user.onboarding

# Extract personalization parameters
prog_exp = onboarding.get("programming_experience", "Intermediate")
robotics_exp = onboarding.get("robotics_experience", "None")
hardware = onboarding.get("hardware_availability", "None")
```

---

### Chapter (EXISTING - file-based)

**Storage**: Markdown files in `docs/chapter-*.md`

**No database table** - chapters are static files loaded from filesystem

**Access Pattern**:

```python
import os

def load_chapter(chapter_id: str) -> str:
    """Load original chapter content from file"""
    file_path = f"docs/{chapter_id}.md"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Chapter {chapter_id} not found")

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

### PersonalizationLog (OPTIONAL - Analytics)

**Purpose**: Track personalization requests for analytics and debugging

**Table Name**: `personalization_log`

**Schema**:

```sql
CREATE TABLE personalization_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    chapter_id VARCHAR(50) NOT NULL,
    transformation_type VARCHAR(100),
    response_time_ms INTEGER,
    cached BOOLEAN DEFAULT FALSE,
    llm_provider VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_log_user ON personalization_log(user_id);
CREATE INDEX idx_log_chapter ON personalization_log(chapter_id);
CREATE INDEX idx_log_created ON personalization_log(created_at DESC);
```

**Usage**:

```python
# Log personalization request
log_entry = PersonalizationLog(
    user_id=user_id,
    chapter_id=chapter_id,
    transformation_type="beginner-simplify",
    response_time_ms=1250,
    cached=False,
    llm_provider="claude"
)
db.add(log_entry)
db.commit()
```

**Analytics Queries**:

```sql
-- Most personalized chapters
SELECT chapter_id, COUNT(*) as requests
FROM personalization_log
GROUP BY chapter_id
ORDER BY requests DESC;

-- Cache hit rate
SELECT
    COUNT(CASE WHEN cached THEN 1 END)::FLOAT / COUNT(*) * 100 as hit_rate_percent
FROM personalization_log;

-- Average response time by cache status
SELECT
    cached,
    AVG(response_time_ms) as avg_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms) as p95_ms
FROM personalization_log
GROUP BY cached;
```

## Database Migration

**Migration Script**: `server/migrations/001_add_personalization_cache.sql`

```sql
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

CREATE INDEX idx_cache_user ON personalization_cache(user_id);
CREATE INDEX idx_cache_chapter ON personalization_cache(chapter_id);
CREATE INDEX idx_cache_profile_hash ON personalization_cache(profile_hash);
CREATE INDEX idx_cache_created ON personalization_cache(created_at DESC);

-- Optional: Add personalization_log table
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

CREATE INDEX idx_log_user ON personalization_log(user_id);
CREATE INDEX idx_log_chapter ON personalization_log(chapter_id);
CREATE INDEX idx_log_created ON personalization_log(created_at DESC);
```

**Run Migration**:

```bash
cd server
python -c "from auth.database import engine; import sqlalchemy; sqlalchemy.text(open('migrations/001_add_personalization_cache.sql').read()).execution_options(autocommit=True).execute(engine)"
```

**Or using Alembic** (if configured):

```bash
alembic revision --autogenerate -m "Add personalization cache"
alembic upgrade head
```

## Storage Estimates

**Per Cached Entry**:
- personalized_content: ~10-50KB (average 30KB)
- Metadata: ~200 bytes
- Total per entry: ~30KB

**Scale**:
- 1,000 users × 10 chapters × 30KB = 300MB
- With 80% cache hit rate: 800 user-chapter pairs cached = 24MB active cache
- Growth: +30KB per new user-chapter combination

**Acceptable** for Postgres storage, fits within free tier limits.

## Performance Considerations

**Cache Lookup**: O(1) with UNIQUE index on (user_id, chapter_id, profile_hash)
**Invalidation**: O(n) where n = number of cached chapters for user/chapter
**Storage Growth**: Linear with user count × active chapters

**Optimization Strategies**:
1. Add TTL-based cleanup (delete entries > 30 days old)
2. Limit cache per user (max 20 chapters cached, LRU eviction)
3. Use Postgres partitioning if cache grows >1M entries

---

**Data Model Status**: ✅ Complete and ready for implementation
