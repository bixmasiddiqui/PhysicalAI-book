# Feature Specification: Urdu Translation System

**Feature ID:** 2-urdu-translation
**Status:** Draft
**Created:** 2025-12-13
**Last Updated:** 2025-12-13
**Owner:** Backend & Frontend Teams
**Stakeholders:** Urdu-speaking students, educators in Pakistan

---

## 1. Overview

### 1.1 Feature Summary

An on-demand translation system that converts Physical AI textbook chapters from English to Urdu while preserving technical terminology, code blocks, and markdown formatting. The system uses LLM-based translation with intelligent caching and a custom glossary to maintain technical accuracy.

### 1.2 Business Value

- **Accessibility**: Makes robotics education accessible to 70M+ Urdu speakers in Pakistan
- **Engagement**: Increases comprehension for students who prefer native language learning
- **Differentiation**: First open-source robotics textbook with native Urdu support
- **Cost Efficiency**: Caching reduces translation API costs by 80%+ for repeated access

### 1.3 Success Metrics

- Translation completes in < 5 seconds for typical chapter (2000-3000 words)
- Cached translations load in < 100ms
- Technical terms preserved with 100% accuracy (based on glossary)
- 90%+ of students report improved comprehension (post-MVP survey)
- Cache hit rate > 70% after 1 week of usage

---

## 2. User Stories

### Priority 1: Core Translation

**US-001: Student Requests Urdu Translation**
```
AS A student with limited English proficiency
I WANT to translate any chapter to Urdu with one click
SO THAT I can learn robotics concepts in my native language
```

**Acceptance Criteria:**
- Toggle button appears on every chapter page
- Clicking "Translate to Urdu" shows loading state
- Translated content appears in < 5 seconds
- Original formatting and code blocks preserved
- Technical terms remain in English (ROS, URDF, etc.)

**US-002: Technical Terms Preservation**
```
AS A student reading translated content
I WANT technical terms to remain in English
SO THAT I can communicate with the global robotics community
```

**Acceptance Criteria:**
- Glossary of 50+ robotics terms maintained
- Terms like ROS, URDF, Gazebo, Python never translated
- Variable names, function names, code preserved
- LaTeX math equations remain unchanged

### Priority 2: Performance & UX

**US-003: Fast Repeated Access**
```
AS A student revisiting a chapter
I WANT previously translated content to load instantly
SO THAT I don't wait for re-translation
```

**Acceptance Criteria:**
- Second request loads from cache in < 100ms
- Cache persists across browser sessions
- Cache shared across all users (not user-specific)
- Cache invalidates when original chapter updated

**US-004: Toggle Between Languages**
```
AS A bilingual student
I WANT to switch between English and Urdu seamlessly
SO THAT I can compare technical explanations
```

**Acceptance Criteria:**
- "Show Original" button appears after translation
- Toggle switches content without re-fetching
- Current language state persists during session
- No page reload required

### Priority 3: Future Enhancements

**US-005: Translation Quality Feedback**
```
AS A student using Urdu translation
I WANT to report translation errors
SO THAT the system improves over time
```

**Acceptance Criteria:**
- "Report Issue" button on translated content
- Feedback stored with chapter_id and error description
- Admin dashboard to review feedback (post-MVP)

---

## 3. Functional Requirements

### FR-001: Translation API Endpoint
- POST /api/translate endpoint accepts chapter_id
- Returns TranslationResponse with Urdu content
- Requires JWT authentication (users must be logged in)
- Supports both original chapters and personalized variants

### FR-002: LLM Integration
- Support for Claude API (primary) and OpenAI (fallback)
- System prompt includes translation guidelines
- Prompt specifies glossary terms to preserve
- Handles 10,000+ word chapters without truncation

### FR-003: Technical Glossary
- JSON glossary file with 50+ terms
- Terms include: ROS, URDF, RVIZ, Gazebo, Python, C++, API, SDK, RPC, ZMP, DOF, IMU, LIDAR, SLAM, PID, DH, FK, IK, URDF, SDF, TF, Twist, Odometry, Quaternion, Euler, Kinematic, Dynamic, Actuator, Encoder, Servo
- Glossary easily extendable via config file
- Case-insensitive matching

### FR-004: Translation Cache
- TranslationCache table stores (chapter_id, language, translated_content)
- MD5 hash of chapter content as version key
- Auto-invalidation when source chapter changes
- Database indexes on (chapter_id, language)

### FR-005: Frontend Toggle Component
- TranslateButton.jsx component similar to PersonalizeButton
- Props: chapterId, originalContent
- States: idle, loading, translated
- Error handling with user-friendly messages

### FR-006: Markdown Preservation
- Code blocks (```python, ```cpp) remain untranslated
- Headers, lists, tables maintain structure
- LaTeX math blocks preserved: $...$, $$...$$
- Links and images remain functional

### FR-007: Fallback Handling
- If translation fails, show original content
- Log error for debugging
- Display user-friendly error message
- No broken states or infinite loading

### FR-008: Analytics & Logging
- Log translation requests (user_id, chapter_id, response_time)
- Track cache hit/miss rates
- Monitor LLM API usage and costs
- TranslationLog table for analytics

---

## 4. Non-Functional Requirements

### NFR-001: Performance
- Fresh translation: p95 < 5 seconds
- Cached translation: p95 < 100ms
- Concurrent translations supported (up to 10 users)

### NFR-002: Reliability
- 99% uptime for translation endpoint
- Graceful degradation if LLM API unavailable
- No data loss in cache

### NFR-003: Security
- JWT authentication required
- Input validation for chapter_id (prevent injection)
- Rate limiting: 20 translations per hour per user

### NFR-004: Maintainability
- Glossary editable without code changes
- Translation prompts configurable via environment
- Modular architecture (translator, cache, routes)

### NFR-005: Cost Efficiency
- Cache hit rate > 70% in steady state
- Estimated cost: $0.01-0.03 per translation
- Monthly budget: < $50 for 1000 active users

---

## 5. Technical Constraints

### TC-001: LLM API Limits
- Claude API: 100K tokens per minute (sufficient)
- OpenAI: 60K tokens per minute
- Need retry logic for rate limit errors

### TC-002: Database Storage
- Each translated chapter ~5-10KB
- 10 chapters × 1000 users = ~50-100MB
- Neon free tier: 3GB (sufficient)

### TC-003: Urdu Font Support
- Requires Unicode UTF-8 encoding
- Noto Nastaliq Urdu font recommended
- Right-to-left (RTL) CSS for proper rendering

---

## 6. Success Criteria

### SC-001: Performance Benchmarks
- ✅ 95% of fresh translations complete in < 5s
- ✅ 99% of cached translations load in < 100ms
- ✅ Cache hit rate > 70% after 1 week

### SC-002: Translation Quality
- ✅ 100% of glossary terms preserved
- ✅ All code blocks remain untranslated
- ✅ Markdown structure intact (headers, lists, tables)
- ✅ No broken links or images

### SC-003: User Experience
- ✅ Toggle button functional on all chapter pages
- ✅ Loading states clear and responsive
- ✅ Error messages helpful (not generic)
- ✅ No crashes or infinite loading states

### SC-004: System Reliability
- ✅ Handles LLM API failures gracefully
- ✅ Concurrent users supported (tested with 10 simultaneous)
- ✅ Cache invalidation works when chapters updated

---

## 7. Edge Cases & Error Handling

### Edge Case 1: Very Long Chapter (>15,000 words)
- **Scenario:** Chapter exceeds LLM context window
- **Handling:** Chunk chapter into sections, translate separately, reassemble
- **Status:** Not implemented in MVP (manual chunking required)

### Edge Case 2: LLM API Down
- **Scenario:** Both Claude and OpenAI APIs unavailable
- **Handling:** Return original content with error message: "Translation temporarily unavailable"
- **Status:** Implemented with fallback logic

### Edge Case 3: Mixed Language Content
- **Scenario:** Chapter already contains Urdu words
- **Handling:** Preserve existing Urdu, translate only English
- **Status:** Best-effort (LLM context-aware)

### Edge Case 4: Special Characters in Code
- **Scenario:** Code blocks with Urdu comments
- **Handling:** Preserve code blocks entirely (no translation inside)
- **Status:** Implemented via prompt engineering

### Edge Case 5: Chapter Updated After Translation
- **Scenario:** Original chapter edited, cached translation outdated
- **Handling:** Recompute MD5 hash, cache miss triggers re-translation
- **Status:** Implemented with content_hash field

### Edge Case 6: User Logs Out Mid-Translation
- **Scenario:** JWT expires during API call
- **Handling:** Return 401, frontend redirects to login
- **Status:** Implemented in auth middleware

---

## 8. Dependencies

### Internal Dependencies
- **Auth System (Step C):** JWT authentication, user sessions
- **Database:** TranslationCache table already exists in database.py
- **Content Personalization (Step D):** Can translate personalized variants

### External Dependencies
- **Claude API:** Primary translation provider
- **OpenAI API:** Fallback translation provider
- **Noto Nastaliq Urdu Font:** For proper rendering (loaded via Google Fonts)

---

## 9. Out of Scope (Post-MVP)

- ❌ Translation to languages other than Urdu (future: Arabic, Hindi)
- ❌ User-submitted glossary corrections (admin-only for now)
- ❌ Audio narration of translated content (TTS integration)
- ❌ Offline translation (requires local LLM)
- ❌ Real-time collaborative translation editing
- ❌ A/B testing between translation prompts

---

## 10. Open Questions

1. **Q:** Should we translate code comments inside code blocks?
   **A:** No - preserve entire code blocks as-is for consistency

2. **Q:** How to handle acronyms not in glossary?
   **A:** LLM will preserve uppercase words by default (prompt engineering)

3. **Q:** Cache per user or globally?
   **A:** Global cache (same translation for all users) to maximize hit rate

4. **Q:** Support translating personalized content?
   **A:** Yes - translate the personalized variant if chapter_id matches

---

## 11. Assumptions

- Users have internet connection (required for API calls)
- Urdu speakers are comfortable with English technical terms (ROS, Python, etc.)
- Chapter updates are infrequent (cache invalidation not a major concern)
- Translation quality improves with LLM model updates (no custom fine-tuning needed)

---

## 12. Risks & Mitigation

### Risk 1: High Translation Costs
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Aggressive caching, monitor usage, set rate limits

### Risk 2: Poor Translation Quality
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Extensive prompt engineering, glossary, user feedback loop

### Risk 3: LLM API Rate Limits
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:** Dual provider support (Claude + OpenAI), exponential backoff retry

### Risk 4: RTL Rendering Issues
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:** Test with Noto Nastaliq font, CSS direction: rtl

---

## Approval

- [ ] Product Owner: _________________
- [ ] Tech Lead: _________________
- [ ] Date: _________________

---

**Next Steps:**
1. Review and approve specification
2. Create implementation plan (/sp.plan)
3. Define API contracts (translate-api.yaml)
4. Implement backend and frontend
5. Test with sample chapters
6. Deploy to production
