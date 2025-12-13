# Implementation Plan: Content Personalization Engine

**Branch**: `1-content-personalization` | **Date**: 2025-12-12 | **Spec**: [spec.md](./spec.md)

## Summary

Build a content personalization system that transforms textbook chapters based on user onboarding profile (programming experience, robotics background, hardware availability). System uses LLM (Claude/OpenAI) to intelligently adapt content difficulty, add/remove examples, and include hardware-specific deployment guides. Personalized content is cached in Postgres for performance (<100ms second request). Frontend provides "Personalize This Chapter" button that requires authentication.

**Technical Approach**: FastAPI backend endpoint receives personalization request → reads user profile from database → constructs structured LLM prompt with transformation rules → calls Claude/OpenAI API → parses and validates response → caches in PersonalizationCache table → returns personalized markdown to frontend → React component displays with toggle option.

## Technical Context

**Language/Version**: Python 3.10+ (backend), JavaScript/React (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy, OpenAI/Anthropic SDKs, Axios (frontend)
**Storage**: Neon Serverless Postgres (PersonalizationCache table, User profiles)
**Testing**: pytest (backend unit/integration), Jest (frontend components)
**Target Platform**: Web application (Docusaurus + FastAPI)
**Project Type**: Web - existing backend/frontend structure
**Performance Goals**:
- LLM transformation: p95 < 3s
- Cache retrieval: p99 < 100ms
- API total: p95 < 500ms (cached)
**Constraints**:
- LLM cost: ~$0.02-0.05 per chapter transformation
- Storage: ~10-50KB per personalized chapter
- Concurrency: 10+ concurrent requests supported
**Scale/Scope**:
- 1000 estimated users
- 10 textbook chapters
- 4 personalization dimensions (experience × 2, hardware, language)

## Constitution Check

**Reviewing against Physical AI Textbook Constitution:**

### ✅ I. User-Centric Design
- **Compliance**: Full compliance - feature adapts to beginner/intermediate/advanced levels, includes hardware-specific guides
- **Verification**: User stories prioritize learning outcomes (P1: beginner/advanced content)

### ✅ II. AI-Native Architecture
- **Compliance**: Uses LLM for content transformation
- **Fallback Required**: ✅ SATISFIED - FR-010 specifies fallback to original content when LLM unavailable
- **Verification**: Error handling returns original chapter with warning message

### ✅ III. API-First Development
- **Compliance**: RESTful endpoint POST /api/personalize with OpenAPI documentation
- **Auth**: ✅ JWT bearer tokens (FR-012 requires authentication)
- **Rate Limiting**: Required for expensive LLM calls - will implement

### ✅ IV. Test-Driven Quality (NON-NEGOTIABLE)
- **Compliance**: Must write tests BEFORE implementation
- **Coverage Target**: 70%+ for transformation logic
- **Test Plan**: Unit tests (transformation rules), integration (API + DB), E2E (button → personalized content)
- **Gate**: Tests written and approved in `/sp.tasks` phase before coding

### ✅ V. Performance & Scalability
- **Compliance**: Caching strategy defined (FR-006, FR-007, FR-008)
- **Targets Met**:
  - ✅ API p95 < 500ms (cached requests)
  - ✅ LLM calls p95 < 3s (within constitution's guidance)
  - ⚠️ Uncached requests ~3s (LLM latency) - acceptable as non-cached is minority case

### ✅ VI. Security & Privacy
- **Compliance**:
  - ✅ JWT authentication required (FR-012)
  - ✅ Input validation (user_id, chapter_id)
  - ✅ SQLAlchemy ORM prevents SQL injection
  - ✅ Markdown sanitization for XSS prevention (to be implemented)
- **Missing**: Rate limiting for LLM endpoint - MUST ADD

### ✅ VII. Simplicity & Maintainability
- **Compliance**:
  - ✅ YAGNI - P1/P2/P3 prioritization allows incremental delivery
  - ✅ DRY - reuses existing auth system, database models
  - ✅ Explicit naming - PersonalizationEngine, TransformationService

**Constitution Gate Status**: ✅ **PASSED** (with action items below)

**Action Items**:
1. Add rate limiting middleware for `/api/personalize` endpoint (10 requests/min per user)
2. Implement markdown sanitization before rendering (XSS prevention)
3. Write tests FIRST in `/sp.tasks` phase (TDD gate)

## Project Structure

### Documentation (this feature)

```text
specs/1-content-personalization/
├── plan.md                  # This file
├── research.md              # Phase 0: LLM prompt engineering, caching strategy
├── data-model.md            # Phase 1: PersonalizationCache schema
├── quickstart.md            # Phase 1: Dev setup and testing guide
├── contracts/               # Phase 1: OpenAPI spec for /api/personalize
│   └── personalize-api.yaml
└── checklists/
    └── requirements.md      # ✅ Already complete
```

### Source Code (repository root)

**Structure Decision**: Web application with existing backend/frontend separation

```text
server/                          # Backend (FastAPI)
├── personalize/                 # NEW: Personalization module
│   ├── __init__.py
│   ├── engine.py                # PersonalizationEngine class
│   ├── transformer.py           # ContentTransformer (LLM integration)
│   ├── cache_manager.py         # CacheManager (DB operations)
│   ├── routes.py                # FastAPI routes
│   └── models.py                # Pydantic request/response models
├── auth/                        # EXISTING: Reuse for authentication
│   └── database.py              # PersonalizationCache table added here
├── main.py                      # MODIFIED: Mount personalize routes
└── tests/                       # NEW: Test files
    ├── test_personalize_engine.py
    ├── test_transformer.py
    ├── test_cache_manager.py
    └── test_personalize_api.py

src/                             # Frontend (React/Docusaurus)
├── components/                  # NEW: React components
│   ├── PersonalizeButton.jsx   # Main button component
│   ├── PersonalizedContent.jsx # Content display with toggle
│   └── __tests__/
│       └── PersonalizeButton.test.jsx
├── theme/                       # MODIFIED: Docusaurus theme customization
│   └── DocItem/
│       └── index.js             # Inject PersonalizeButton
└── css/                         # MODIFIED: Styling
    └── personalize.css

docs/                            # EXISTING: Original chapters (unchanged)
└── chapter-*.md                 # Source content

.env.example                     # MODIFIED: Add personalization config
```

## Complexity Tracking

**No constitution violations requiring justification.**

All complexity is necessary for core feature functionality:
- LLM integration: Required for intelligent content transformation
- Caching layer: Required for performance (<100ms target)
- Frontend/backend separation: Existing architecture pattern

## Phase 0: Research & Unknowns

### Research Tasks

1. **LLM Prompt Engineering for Content Transformation**
   - **Question**: What prompt structure produces reliable, consistent transformations?
   - **Approach**: Test prompts with Claude/OpenAI for beginner→advanced transformations
   - **Deliverable**: Tested prompt template with examples

2. **Caching Strategy & Invalidation**
   - **Question**: When should cache be invalidated? How to handle chapter updates?
   - **Approach**: Design cache key structure (user_id + chapter_id + profile_hash)
   - **Deliverable**: Cache invalidation rules and database indexes

3. **Markdown Preservation During Transformation**
   - **Question**: How to ensure code blocks, links, images remain intact?
   - **Approach**: Test LLM instruction to preserve markdown syntax
   - **Deliverable**: Validation regex patterns for markdown integrity

4. **Performance Optimization for Long Chapters**
   - **Question**: How to handle chapters >10,000 words without timeout?
   - **Approach**: Research chunking strategy or streaming responses
   - **Deliverable**: Chunking algorithm or async processing design

5. **Rate Limiting Strategy**
   - **Question**: What limits prevent abuse while allowing legitimate use?
   - **Approach**: Analyze typical usage patterns, LLM cost per request
   - **Deliverable**: Rate limit configuration (requests/min per user/IP)

**Output**: `research.md` with findings and decisions

## Phase 1: Design & Contracts

### Data Model

**File**: `data-model.md`

**Entities**:

1. **PersonalizationCache** (new table in Neon Postgres)
   ```
   Attributes:
   - id: SERIAL PRIMARY KEY
   - user_id: INTEGER REFERENCES users(id)
   - chapter_id: VARCHAR(50) (e.g., "chapter-01")
   - profile_hash: VARCHAR(64) (hash of onboarding JSON for cache key)
   - personalized_content: TEXT
   - created_at: TIMESTAMP DEFAULT NOW()
   - version: INTEGER DEFAULT 1

   Indexes:
   - UNIQUE(user_id, chapter_id, profile_hash)
   - INDEX(user_id)
   - INDEX(chapter_id)

   Relationships:
   - belongs_to User (auth.database.User)
   ```

2. **User Profile** (existing - reuse from Step C)
   ```
   Attributes used:
   - onboarding.programming_experience
   - onboarding.robotics_experience
   - onboarding.hardware_availability
   - onboarding.preferred_language
   ```

3. **PersonalizationLog** (optional analytics table)
   ```
   Attributes:
   - id: SERIAL PRIMARY KEY
   - user_id: INTEGER
   - chapter_id: VARCHAR(50)
   - transformation_type: VARCHAR(50) (e.g., "beginner-simplify")
   - response_time_ms: INTEGER
   - cached: BOOLEAN
   - created_at: TIMESTAMP
   ```

### API Contracts

**File**: `contracts/personalize-api.yaml` (OpenAPI 3.0)

**Endpoints**:

1. **POST /api/personalize**
   ```yaml
   summary: Personalize chapter content for authenticated user
   security:
     - bearerAuth: []
   requestBody:
     required: true
     content:
       application/json:
         schema:
           type: object
           required: [chapter_id]
           properties:
             chapter_id:
               type: string
               example: "chapter-01"
               description: Chapter identifier
   responses:
     200:
       description: Personalized content returned
       content:
         application/json:
           schema:
             type: object
             properties:
               original_chapter_id:
                 type: string
               personalized_variant_id:
                 type: string
               content:
                 type: string
                 description: Personalized markdown
               applied_transformations:
                 type: array
                 items:
                   type: string
                 example: ["beginner-simplify", "no-hardware-simulator"]
               cached:
                 type: boolean
               metadata:
                 type: object
                 properties:
                   processing_time_ms:
                     type: integer
                   profile_hash:
                     type: string
     401:
       description: Unauthorized - user not authenticated
     404:
       description: Chapter not found
     429:
       description: Rate limit exceeded
     500:
       description: LLM service unavailable (returns original content)
   ```

2. **GET /api/personalize/cache-stats** (optional, for debugging)
   ```yaml
   summary: Get cache statistics for authenticated user
   responses:
     200:
       description: Cache statistics
       content:
         application/json:
           schema:
             type: object
             properties:
               total_cached:
                 type: integer
               hit_rate:
                 type: number
               chapters_cached:
                 type: array
   ```

### Quickstart Guide

**File**: `quickstart.md`

```markdown
# Personalization Engine - Developer Quickstart

## Prerequisites
- Step C (Authentication) completed and working
- Database initialized with users table
- LLM API key configured (CLAUDE_API_KEY or OPENAI_API_KEY)

## Setup

1. Add PersonalizationCache table:
   ```bash
   cd server
   python -c "from auth.database import init_db; init_db()"
   ```

2. Install dependencies:
   ```bash
   pip install anthropic==0.8.1 openai==1.10.0
   ```

3. Configure environment:
   ```bash
   echo "PERSONALIZE_RATE_LIMIT=10" >> .env
   echo "PERSONALIZE_CACHE_TTL=86400" >> .env
   ```

## Run Tests

```bash
pytest server/tests/test_personalize_*.py -v
```

## Manual Testing

1. Start server: `python server/main.py`
2. Signup user: `POST /auth/signup` with beginner profile
3. Login: `POST /auth/login` → get token
4. Personalize: `POST /api/personalize -H "Authorization: Bearer <token>" -d '{"chapter_id":"chapter-01"}'`
5. Verify cached: Repeat step 4, check `cached:true` in response

## Debugging

- Check logs: `tail -f server/logs/personalize.log`
- View cache: `SELECT * FROM personalization_cache WHERE user_id=1;`
- Clear cache: `DELETE FROM personalization_cache;`
```

## Architecture Decisions

### Decision 1: LLM Provider Strategy

**Options Considered**:
1. Claude only (Anthropic)
2. OpenAI only
3. Dual support with fallback

**Choice**: **Dual support** - use environment variable to select, fallback if primary fails

**Rationale**:
- Claude excels at instruction following for transformations
- OpenAI has better availability/lower latency in some regions
- Cost optimization: switch based on pricing changes
- Resilience: fallback if one service is down

**Implementation**: `transformer.py` checks `LLM_PROVIDER` env var, instantiates appropriate client

---

### Decision 2: Caching Granularity

**Options Considered**:
1. Cache entire personalized chapter
2. Cache transformation rules only (reapply on demand)
3. Cache by section/paragraph

**Choice**: **Cache entire chapter**

**Rationale**:
- Simplicity: Single DB write/read operation
- Performance: <100ms retrieval (SC-002 requirement)
- Storage acceptable: 50KB × 1000 users × 10 chapters = 500MB total
- Invalidation straightforward: Delete row on profile change

**Trade-off**: Higher storage, but meets performance targets

---

### Decision 3: Profile Hash for Cache Key

**Options Considered**:
1. Use user_id + chapter_id only
2. Use user_id + chapter_id + profile_hash
3. Use user_id + chapter_id + individual field values

**Choice**: **profile_hash** (MD5 of sorted onboarding JSON)

**Rationale**:
- Handles profile updates correctly (new hash = new cache entry)
- Multiple users with identical profiles share cache (cost savings)
- Simpler than tracking individual field changes

**Implementation**:
```python
import hashlib
import json

def compute_profile_hash(onboarding: dict) -> str:
    sorted_json = json.dumps(onboarding, sort_keys=True)
    return hashlib.md5(sorted_json.encode()).hexdigest()
```

---

### Decision 4: Frontend Integration Point

**Options Considered**:
1. Custom Docusaurus plugin
2. Theme swizzling (modify DocItem component)
3. Standalone widget injected via script

**Choice**: **Theme swizzling** (modify `src/theme/DocItem/index.js`)

**Rationale**:
- Native Docusaurus integration (no external scripts)
- Access to page context (chapter ID, user auth state)
- Consistent with Docusaurus architecture patterns
- Easy to maintain across Docusaurus upgrades

**Implementation**: Swizzle DocItem, inject `<PersonalizeButton />` component above content

---

### Decision 5: Markdown Sanitization Strategy

**Options Considered**:
1. Trust LLM output completely
2. Parse and validate markdown structure
3. Use markdown sanitizer library (DOMPurify)

**Choice**: **Validate + DOMPurify sanitization**

**Rationale**:
- Security: Prevent XSS if LLM injects malicious HTML
- Reliability: Catch malformed markdown before rendering
- Constitution requirement: Sanitize markdown (Principle VI)

**Implementation**: Use `markdown-it` to parse, `dompurify` to sanitize, validate code block integrity

## Next Steps

1. Complete Phase 0 Research: Run research tasks, document findings in `research.md`
2. Complete Phase 1 Design: Create `data-model.md`, `contracts/personalize-api.yaml`, `quickstart.md`
3. Run `/sp.tasks`: Generate testable task list (TDD - write tests first)
4. Implement (Red-Green-Refactor cycle)
5. Deploy and validate against success criteria

---

**Plan Status**: ✅ Ready for Phase 0 Research

**Next Command**: Begin research or proceed directly to `/sp.tasks` if research is not needed
