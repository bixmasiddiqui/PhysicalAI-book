# Physical AI Textbook Constitution

**Project:** Physical AI & Humanoid Robotics Interactive Textbook
**Purpose:** Educational platform with AI-powered features for personalized learning

## Core Principles

### I. User-Centric Design
All features must serve educational goals and improve learning outcomes. Content adapts to user's experience level (beginner → intermediate → advanced), background, and available resources. Accessibility across devices and languages. Progressive disclosure of complexity.

### II. AI-Native Architecture
Leverage AI throughout the platform while maintaining reliability:
- RAG Chatbot: Context-aware answers from textbook content
- Claude Code Subagents: Reusable skills (summarization, quiz generation, code explanation)
- Content Personalization: LLM-driven content transformation based on user profile
- Translation: AI-powered multilingual support with technical accuracy
- **Fallbacks Required:** All AI features must have graceful degradation paths

### III. API-First Development
Backend services expose clean, documented APIs. RESTful design with clear resource naming. OpenAPI/Swagger documentation auto-generated. URL-based versioning for breaking changes. Consistent error taxonomy. JWT bearer token authentication. Rate limiting to protect against abuse.

### IV. Test-Driven Quality (NON-NEGOTIABLE)
TDD mandatory for all new features:
- Unit tests cover business logic, transformations, parsing (70%+ coverage target)
- Integration tests for API endpoints, database operations, AI service calls
- E2E tests for critical user flows (signup → personalize → query)
- CI enforcement: All tests must pass before merge
- No merge without tests

### V. Performance & Scalability
Design for production-ready performance:
- **Caching:** Personalized content, translations, RAG embeddings cached
- **Database:** Neon Serverless Postgres with connection pooling
- **Vector DB:** Qdrant for scalable semantic search
- **Targets:** API p95 < 500ms (excluding LLM calls), LLM calls p95 < 3s, Page load < 2s

### VI. Security & Privacy
Protect user data and maintain trust. JWT authentication (7-day expiration). bcrypt password hashing (cost factor 12). Never commit API keys. Validate all user inputs server-side. Use parameterized queries (SQLAlchemy ORM). Sanitize markdown content before rendering. Whitelist CORS origins. Rate limit expensive AI endpoints.

### VII. Simplicity & Maintainability
YAGNI principles: Don't build features we don't need now. DRY: Extract common patterns. Explicit over implicit naming. Document setup in README, complex functions with docstrings. Code reviews required for all changes.

## Technology Stack

**Backend:** FastAPI 0.109+, Python 3.10+ (type hints required), Neon Serverless Postgres, SQLAlchemy 2.0+, JWT (python-jose, passlib), Claude/OpenAI APIs, Qdrant Cloud

**Frontend:** Docusaurus 3.x, JavaScript/TypeScript, CSS Modules, React Context for auth, Axios for HTTP

**Infrastructure:** Vercel (preferred) or separate deployment, GitHub Actions for CI/CD, `.env` files with validation, GitHub Secrets for CI

## Development Workflow

1. **Spec First:** Create feature spec with `/sp.specify <description>`
2. **Plan:** Generate architectural plan with `/sp.plan`
3. **Tasks:** Break into testable tasks with `/sp.tasks`
4. **TDD:** Write tests → make them pass → refactor
5. **Review:** Code review before merge
6. **Deploy:** Automated via CI/CD

**Branch Strategy:** `main` (production), feature branches `<number>-<feature-name>`. No direct commits to main.

## Quality Gates

**Pre-Merge:** All tests pass, no linter errors, coverage ≥ 70%, API docs updated, no secrets in commits

**Pre-Deploy:** CI pipeline passes, smoke tests on staging, database migrations applied, environment variables configured, health check returns 200

## Governance

Constitution supersedes all conflicting practices. Amendments require documented rationale, approval, migration plan. Quarterly review and updates. Exceptions require ADR (Architecture Decision Record) with justification.

**Version**: 1.0.0 | **Ratified**: 2025-12-12 | **Last Amended**: 2025-12-12
