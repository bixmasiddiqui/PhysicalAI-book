# Content Personalization - Developer Quickstart

**Feature**: Content Personalization Engine
**Prerequisites**: Step C (Authentication) completed, database initialized

## Overview

This quickstart guide helps you:
1. Set up the personalization backend
2. Run the database migration
3. Test personalization endpoints locally
4. Integrate the frontend button component

**Estimated Time**: 15-20 minutes

---

## Prerequisites Checklist

- [x] Step C (Authentication) working: `/auth/signup` and `/auth/login` functional
- [x] Database initialized with `users` table
- [x] Environment variables configured (`.env` file exists)
- [x] LLM API key available (Claude or OpenAI)

**Verify Prerequisites**:

```bash
# Test auth endpoints
curl http://localhost:8000/auth/health
# Expected: {"status":"ok","module":"authentication",...}

# Check database connection
cd server
python -c "from auth.database import SessionLocal; db = SessionLocal(); print('DB connected')"
# Expected: "DB connected"
```

---

## Setup Instructions

### 1. Add Database Migration

Create the `personalization_cache` table:

```bash
cd server
```

**Create migration file**:

```bash
mkdir -p migrations
cat > migrations/001_add_personalization_cache.sql << 'EOF'
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
EOF
```

**Run migration**:

```bash
python -c "
from auth.database import engine
from sqlalchemy import text

with open('migrations/001_add_personalization_cache.sql') as f:
    sql = f.read()

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

print('✅ Migration complete: personalization_cache table created')
"
```

**Verify**:

```bash
python -c "
from auth.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

if 'personalization_cache' in tables:
    print('✅ personalization_cache table exists')
    columns = [col['name'] for col in inspector.get_columns('personalization_cache')]
    print(f'   Columns: {columns}')
else:
    print('❌ Table not found')
"
```

**Expected Output**:
```
✅ personalization_cache table exists
   Columns: ['id', 'user_id', 'chapter_id', 'profile_hash', 'personalized_content', 'applied_transformations', 'created_at', 'version']
```

---

### 2. Install Additional Dependencies

```bash
pip install anthropic==0.8.1 openai==1.10.0
```

**Verify installation**:

```bash
python -c "import anthropic, openai; print('✅ LLM SDKs installed')"
```

---

### 3. Configure Environment Variables

Add personalization config to `.env`:

```bash
cd ..  # Back to project root
echo "" >> .env
echo "# Personalization Configuration" >> .env
echo "LLM_PROVIDER=claude" >> .env
echo "PERSONALIZE_RATE_LIMIT=10" >> .env
echo "PERSONALIZE_CACHE_TTL=86400" >> .env
```

**Verify**:

```bash
cat .env | grep -E "(LLM_PROVIDER|PERSONALIZE)"
```

**Expected**:
```
LLM_PROVIDER=claude
PERSONALIZE_RATE_LIMIT=10
PERSONALIZE_CACHE_TTL=86400
```

---

### 4. Create Personalization Module Structure

```bash
cd server
mkdir -p personalize
touch personalize/__init__.py
touch personalize/engine.py
touch personalize/transformer.py
touch personalize/cache_manager.py
touch personalize/routes.py
touch personalize/models.py
```

**Verify structure**:

```bash
ls -la personalize/
```

**Expected**:
```
__init__.py
cache_manager.py
engine.py
models.py
routes.py
transformer.py
```

---

## Testing Guide

### Manual API Testing

**Step 1: Start Server**

```bash
cd server
python main.py
```

**Expected**:
```
Starting Physical AI Textbook API Server...
Environment: development
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

**Step 2: Create Test User (in new terminal)**

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "beginner@test.com",
    "password": "testpass123",
    "onboarding": {
      "role": "Student",
      "programming_experience": "Beginner",
      "robotics_experience": "None",
      "preferred_language": "English",
      "hardware_availability": "None"
    }
  }'
```

**Expected Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "beginner@test.com"
}
```

**Save the token**:
```bash
export TOKEN="<paste_access_token_here>"
```

---

**Step 3: Request Personalized Content**

```bash
curl -X POST http://localhost:8000/api/personalize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": "chapter-01"}'
```

**Expected Response** (first request - uncached):
```json
{
  "original_chapter_id": "chapter-01",
  "personalized_variant_id": "chapter-01-user-1-v1-a7f3e2",
  "content": "# Fundamentals of Physical AI (Simplified for Beginners)...",
  "applied_transformations": ["beginner-simplify", "add-examples"],
  "cached": false,
  "metadata": {
    "processing_time_ms": 2350,
    "profile_hash": "a7f3e2b1c4d5e6f7",
    "llm_provider": "claude",
    "fallback_used": false
  }
}
```

---

**Step 4: Verify Caching (repeat request)**

```bash
curl -X POST http://localhost:8000/api/personalize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chapter_id": "chapter-01"}'
```

**Expected Response** (second request - cached):
```json
{
  ...
  "cached": true,
  "metadata": {
    "processing_time_ms": 45,  // << Fast!
    ...
  }
}
```

✅ **Success**: `cached: true` and `processing_time_ms < 100`

---

**Step 5: Check Cache Stats**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/personalize/cache-stats
```

**Expected**:
```json
{
  "total_cached": 1,
  "hit_rate": 50.0,
  "chapters_cached": ["chapter-01"],
  "total_size_kb": 30,
  "last_updated": "2025-12-12T10:30:00Z"
}
```

---

### Automated Testing

**Create test file**:

```bash
cd server
cat > tests/test_personalize_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_personalize_requires_auth():
    """Test that personalization requires authentication"""
    response = client.post("/api/personalize", json={"chapter_id": "chapter-01"})
    assert response.status_code == 401

def test_personalize_invalid_chapter():
    """Test 404 for non-existent chapter"""
    # TODO: Add after auth is implemented
    pass

def test_personalize_success():
    """Test successful personalization"""
    # TODO: Implement after routes are created
    pass
EOF
```

**Run tests**:

```bash
pytest tests/test_personalize_api.py -v
```

---

## Debugging

### Check Database Cache

```bash
python -c "
from auth.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('SELECT user_id, chapter_id, cached_at FROM personalization_cache')).fetchall()

print('Cached entries:')
for row in result:
    print(f'  User {row[0]} | Chapter {row[1]} | Cached at {row[2]}')
"
```

---

### Clear Cache (for testing)

```bash
python -c "
from auth.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text('DELETE FROM personalization_cache'))
db.commit()

print('✅ Cache cleared')
"
```

---

### View Logs

```bash
# If using file logging
tail -f server/logs/personalize.log

# Or check stdout
# Server logs appear in terminal where python main.py is running
```

---

## Frontend Integration (Preview)

**Button Component Location**: `src/components/PersonalizeButton.jsx`

**Integration Point**: `src/theme/DocItem/index.js` (Docusaurus theme)

**Quick Test** (after implementation):

1. Start frontend: `npm start`
2. Navigate to http://localhost:3000/docs/chapter-01
3. Look for "Personalize This Chapter" button
4. Click → Should prompt login if not authenticated
5. After login → Content should transform

---

## Troubleshooting

### Problem: Migration fails with "table already exists"

**Solution**:
```bash
python -c "
from auth.database import engine
from sqlalchemy import text

engine.execute(text('DROP TABLE IF EXISTS personalization_cache CASCADE'))
print('Table dropped. Re-run migration.')
"
```

---

### Problem: LLM API returns 401 Unauthorized

**Solution**:
```bash
# Check API key is set
env | grep -E "(CLAUDE_API_KEY|OPENAI_API_KEY)"

# Test API key
python -c "
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
message = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print('✅ API key valid')
"
```

---

### Problem: Cache always shows cached:false

**Check**: Is profile_hash being computed correctly?

```bash
python -c "
import hashlib
import json

onboarding = {
    'role': 'Student',
    'programming_experience': 'Beginner',
    'robotics_experience': 'None',
    'preferred_language': 'English',
    'hardware_availability': 'None'
}

sorted_json = json.dumps(onboarding, sort_keys=True)
profile_hash = hashlib.md5(sorted_json.encode()).hexdigest()

print(f'Profile hash: {profile_hash}')
print('Check this appears in database')
"
```

---

## Next Steps

1. ✅ Database migrated
2. ✅ Dependencies installed
3. ✅ Manual testing successful
4. ⏭️ Run `/sp.tasks` to generate implementation tasks
5. ⏭️ Implement TDD: Write tests first, then code
6. ⏭️ Integrate frontend button component

---

**Quickstart Status**: ✅ Complete and ready for development
