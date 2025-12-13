# Implementation Plan: Urdu Translation System

**Feature ID:** 2-urdu-translation
**Plan Status:** Ready for Implementation
**Created:** 2025-12-13
**Estimated Effort:** 3-4 hours

---

## 1. Technical Context

### Existing Infrastructure
- **Database:** TranslationCache table already exists in `server/auth/database.py`
- **Auth System:** JWT authentication via `get_current_user` dependency
- **LLM Integration:** Pattern established in `server/personalize/transformer.py`
- **Frontend Pattern:** React component pattern from `src/components/PersonalizeButton.jsx`

### New Components to Build
1. `server/translate/` module (routes, translator, cache_manager, models)
2. `src/components/TranslateButton.jsx` (React component)
3. `server/translate/glossary.json` (technical terms)
4. Database migration (if TranslationCache schema needs updates)

---

## 2. Architecture Decisions

### Decision 1: Global vs Per-User Cache

**Options Considered:**
- A) Cache per user (cache key: user_id + chapter_id + language)
- B) Global cache (cache key: chapter_id + language + content_hash)

**Decision:** **B) Global cache**

**Rationale:**
- Same Urdu translation serves all users (not personalized)
- Maximizes cache hit rate (70%+ vs 20-30% with per-user)
- Reduces API costs significantly
- Content hash ensures cache invalidation when chapter updates

**Implementation:**
```python
cache_key = f"{chapter_id}_{language}_{content_hash[:8]}"
```

### Decision 2: Translation Chunking Strategy

**Options Considered:**
- A) Translate entire chapter in one API call
- B) Chunk into sections (headers), translate separately
- C) Dynamic chunking based on token count

**Decision:** **A) Translate entire chapter (with fallback to B for >15K words)**

**Rationale:**
- Most chapters are 2000-5000 words (well within LLM limits)
- Single API call maintains context and coherence
- Chunking only for edge cases (manually triggered)

**Implementation:**
- Default: Single API call
- If content > 15,000 words: Return error asking to contact admin
- Future: Implement auto-chunking

### Decision 3: Glossary Management

**Options Considered:**
- A) Hardcoded list in Python file
- B) JSON config file
- C) Database table (admin UI to edit)

**Decision:** **B) JSON config file**

**Rationale:**
- Easy to edit without code changes
- Version controlled in Git
- Fast loading (no DB query)
- Post-MVP: Migrate to database with admin UI

**Implementation:**
```json
{
  "robotics_terms": ["ROS", "URDF", "RVIZ", "Gazebo", ...],
  "programming_terms": ["Python", "C++", "API", "SDK", ...],
  "math_terms": ["ZMP", "DOF", "DH", "FK", "IK", ...]
}
```

### Decision 4: LLM Provider Strategy

**Options Considered:**
- A) Claude only
- B) OpenAI only
- C) Claude primary, OpenAI fallback

**Decision:** **C) Claude primary, OpenAI fallback**

**Rationale:**
- Claude excels at instruction following (glossary preservation)
- OpenAI fallback ensures 99% uptime
- Reuse pattern from personalization module

**Implementation:**
```python
try:
    translation = await self._call_claude(prompt)
except Exception:
    translation = await self._call_openai(prompt)
```

### Decision 5: Frontend Component Integration

**Options Considered:**
- A) Inline toggle in chapter (Docusaurus swizzling)
- B) Separate component above content
- C) Floating action button

**Decision:** **B) Separate component above content (MVP), then A)**

**Rationale:**
- Quick to implement without Docusaurus theme modifications
- Reuses PersonalizeButton pattern
- Post-MVP: Integrate into Docusaurus theme like PersonalizeButton

---

## 3. Implementation Tasks

### Phase 1: Backend Foundation (60 min)

**Task 1.1: Database Verification**
- [ ] Check if TranslationCache table has `content_hash` field
- [ ] Add migration if needed: `002_add_content_hash_to_translation_cache.sql`
- [ ] Verify indexes on (chapter_id, language, content_hash)

**Task 1.2: Create Translation Module Structure**
```bash
server/translate/
├── __init__.py
├── models.py          # Pydantic models
├── translator.py      # LLM translation logic
├── cache_manager.py   # Database caching
├── routes.py          # FastAPI endpoints
└── glossary.json      # Technical terms
```

**Task 1.3: Implement Models (models.py)**
```python
class TranslateRequest(BaseModel):
    chapter_id: str
    target_language: str = "urdu"
    source_content: Optional[str] = None  # For personalized variants

class TranslateResponse(BaseModel):
    original_chapter_id: str
    target_language: str
    translated_content: str
    cached: bool
    metadata: Dict[str, Any]
```

**Task 1.4: Create Technical Glossary (glossary.json)**
- Compile 50+ robotics/programming terms
- Organized by category
- Include variations (ROS2, ros, ROS1)

### Phase 2: Translation Logic (90 min)

**Task 2.1: Implement CacheManager (cache_manager.py)**
```python
class TranslationCacheManager:
    def compute_content_hash(self, content: str) -> str:
        """MD5 hash of chapter content"""

    def get_cached_translation(self, chapter_id, language, content_hash):
        """Retrieve from database"""

    def save_translation(self, chapter_id, language, content_hash, translated_content):
        """Save to database"""

    def invalidate_cache(self, chapter_id):
        """Clear cache for updated chapter"""
```

**Task 2.2: Implement Translator (translator.py)**
```python
class UrduTranslator:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "claude")
        self.glossary = self.load_glossary()

    def load_glossary(self) -> dict:
        """Load from glossary.json"""

    def build_translation_prompt(self, content: str, glossary: dict) -> str:
        """Construct LLM prompt with preservation rules"""

    async def translate(self, content: str, target_language: str) -> str:
        """Main translation method"""

    async def _call_claude(self, prompt: str) -> str:
        """Claude API integration"""

    async def _call_openai(self, prompt: str) -> str:
        """OpenAI API integration"""
```

**Task 2.3: Prompt Engineering**
Key prompt elements:
- Translate English to Urdu
- Preserve technical terms from glossary
- Keep code blocks untranslated
- Maintain markdown structure
- Preserve LaTeX equations
- Natural Urdu (not literal word-by-word)

Example prompt:
```
You are an expert translator specializing in technical content. Translate the following robotics textbook chapter from English to Urdu.

CRITICAL RULES:
1. NEVER translate these technical terms: {glossary_terms}
2. NEVER translate content inside code blocks (```...```)
3. NEVER translate LaTeX equations ($...$)
4. Preserve all markdown formatting (headers, lists, links, images)
5. Use natural, fluent Urdu (not literal translation)
6. Keep variable names, function names, file paths in English

Content to translate:
{content}

Return ONLY the translated markdown. Do not add explanations or notes.
```

### Phase 3: API Routes (30 min)

**Task 3.1: Implement Routes (routes.py)**
```python
@router.post("/translate", response_model=TranslateResponse)
async def translate_chapter(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Translate chapter to target language"""

@router.get("/translate/cache-stats")
async def get_translation_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get translation cache statistics"""

@router.delete("/translate/cache/{chapter_id}")
async def invalidate_translation_cache(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invalidate cache for specific chapter (admin only)"""
```

**Task 3.2: Mount Router in main.py**
```python
from translate.routes import router as translate_router
app.include_router(translate_router, prefix="/api", tags=["Translation"])
```

### Phase 4: Frontend Component (45 min)

**Task 4.1: Create TranslateButton Component**
```javascript
// src/components/TranslateButton.jsx
const TranslateButton = ({ chapterId, originalContent }) => {
  const [loading, setLoading] = useState(false);
  const [translated, setTranslated] = useState(false);
  const [urduContent, setUrduContent] = useState(null);
  const [error, setError] = useState(null);

  const handleTranslate = async () => {
    // Check auth
    // Call /api/translate
    // Handle response
  };

  const handleToggle = () => {
    setTranslated(!translated);
  };

  return (
    <div className="translation-container">
      <button onClick={handleTranslate}>
        {loading ? 'Translating...' : 'Translate to Urdu'}
      </button>
      {translated && (
        <>
          <button onClick={handleToggle}>
            {translated ? 'Show Original' : 'Show Urdu'}
          </button>
          <div className="urdu-content" dir="rtl" lang="ur">
            {urduContent}
          </div>
        </>
      )}
    </div>
  );
};
```

**Task 4.2: Add Urdu Font Support**
- Add Google Fonts link to Docusaurus config
- CSS for RTL rendering
```css
.urdu-content {
  direction: rtl;
  font-family: 'Noto Nastaliq Urdu', serif;
  text-align: right;
  line-height: 2;
}
```

### Phase 5: Testing & Validation (45 min)

**Task 5.1: Manual Testing**
- [ ] Test translation with chapter-01.md
- [ ] Verify technical terms preserved
- [ ] Check code blocks untranslated
- [ ] Confirm cache hit on second request
- [ ] Test toggle between English/Urdu
- [ ] Verify RTL rendering

**Task 5.2: Edge Case Testing**
- [ ] Long chapter (>10,000 words)
- [ ] Chapter with LaTeX equations
- [ ] Chapter with mixed code languages (Python + C++)
- [ ] LLM API failure (disable API key temporarily)
- [ ] Concurrent requests (10 users)

**Task 5.3: Performance Testing**
- [ ] Measure fresh translation time (target: < 5s)
- [ ] Measure cached translation time (target: < 100ms)
- [ ] Check database query performance
- [ ] Monitor LLM token usage

---

## 4. Database Schema Updates

### Check Existing TranslationCache Table

Current schema (from `server/auth/database.py`):
```python
class TranslationCache(Base):
    __tablename__ = "translation_cache"
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(String(50), index=True, nullable=False)
    language = Column(String(10), index=True, nullable=False)
    translated_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Missing Fields:**
- `content_hash` (for cache invalidation)
- `version` (for future schema evolution)

### Migration: 002_add_content_hash.sql
```sql
-- Add content_hash field for cache invalidation
ALTER TABLE translation_cache
ADD COLUMN content_hash VARCHAR(64);

-- Create index for faster lookups
CREATE INDEX idx_translation_cache_hash
ON translation_cache(chapter_id, language, content_hash);

-- Add version field
ALTER TABLE translation_cache
ADD COLUMN version INTEGER DEFAULT 1;
```

---

## 5. API Contracts

See `contracts/translate-api.yaml` for full OpenAPI specification.

**Key Endpoints:**

1. **POST /api/translate**
   - Request: `{ chapter_id, target_language, source_content? }`
   - Response: `{ translated_content, cached, metadata }`
   - Auth: JWT required
   - Rate limit: 20/hour per user

2. **GET /api/translate/cache-stats**
   - Response: `{ total_cached, languages, hit_rate, total_size_kb }`
   - Auth: JWT required

---

## 6. Configuration

### Environment Variables
```bash
# .env additions
LLM_PROVIDER=claude  # or openai
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Translation settings
DEFAULT_TARGET_LANGUAGE=urdu
TRANSLATION_CACHE_TTL=2592000  # 30 days
```

### Glossary Configuration
Location: `server/translate/glossary.json`
```json
{
  "version": "1.0",
  "last_updated": "2025-12-13",
  "categories": {
    "robotics": ["ROS", "ROS2", "URDF", "RVIZ", "Gazebo", "MoveIt", "TF", "SLAM"],
    "programming": ["Python", "C++", "JavaScript", "API", "SDK", "Git", "Docker"],
    "hardware": ["Arduino", "Raspberry Pi", "Jetson", "IMU", "LIDAR", "Servo"],
    "math": ["ZMP", "DOF", "DH", "FK", "IK", "Jacobian", "Quaternion", "Euler"],
    "formats": ["JSON", "YAML", "XML", "CSV", "Markdown"]
  }
}
```

---

## 7. Dependencies

### Python Packages (already installed from Step D)
- `anthropic==0.8.1`
- `openai==1.10.0`
- `fastapi`
- `sqlalchemy`

### New Dependencies
- None (reuse existing)

### Frontend Dependencies
- `@fontsource/noto-nastaliq-urdu` (optional, can use Google Fonts CDN)

---

## 8. Rollout Plan

### Phase 1: Backend Deployment
1. Run database migration
2. Deploy backend code to server
3. Test with curl/Postman
4. Verify caching works

### Phase 2: Frontend Integration
1. Add TranslateButton component
2. Test with dev server
3. Deploy to production
4. Monitor error logs

### Phase 3: Monitoring
1. Set up Sentry error tracking
2. Monitor LLM API costs (set budget alerts)
3. Track cache hit rate (target: >70%)
4. Collect user feedback

---

## 9. Success Criteria Checklist

- [ ] **SC-001:** Fresh translation completes in < 5s (95th percentile)
- [ ] **SC-002:** Cached translation loads in < 100ms (99th percentile)
- [ ] **SC-003:** 100% of glossary terms preserved in translation
- [ ] **SC-004:** All code blocks remain untranslated
- [ ] **SC-005:** Markdown structure intact (headers, lists, tables, links)
- [ ] **SC-006:** RTL rendering correct in Urdu content
- [ ] **SC-007:** Toggle between English/Urdu functional
- [ ] **SC-008:** Graceful error handling when LLM API fails
- [ ] **SC-009:** Cache invalidation works when chapter updated
- [ ] **SC-010:** Rate limiting prevents abuse (20/hour per user)

---

## 10. Risks & Mitigation

### Risk 1: Translation Quality Issues
- **Mitigation:** Extensive prompt testing, A/B test different prompts
- **Fallback:** Manual review process for first 5 chapters

### Risk 2: High API Costs
- **Mitigation:** Aggressive caching, rate limits, budget alerts
- **Monitoring:** Track cost per translation, set $100/month limit

### Risk 3: Font Rendering Issues
- **Mitigation:** Test on Windows, Mac, Linux, mobile browsers
- **Fallback:** Use Google Fonts CDN with fallback to system fonts

---

## 11. Timeline Estimate

- **Phase 1 (Backend):** 60 minutes
- **Phase 2 (Translation Logic):** 90 minutes
- **Phase 3 (API Routes):** 30 minutes
- **Phase 4 (Frontend):** 45 minutes
- **Phase 5 (Testing):** 45 minutes
- **Total:** ~4 hours

---

## 12. Next Steps

1. ✅ Review and approve plan
2. ⏳ Create API contract (translate-api.yaml)
3. ⏳ Implement backend (server/translate/)
4. ⏳ Implement frontend (TranslateButton.jsx)
5. ⏳ Test with sample chapters
6. ⏳ Deploy and monitor

---

**Plan Approved By:**
- [ ] Tech Lead: _________________
- [ ] Date: _________________
