# Project Structure - Physical AI Textbook

## Overview

This project has been refactored into a clean, modular structure with separated frontend and backend.

## Directory Tree

```
physical-AI/
│
├── frontend/                           # FRONTEND (Docusaurus)
│   ├── docs/                          # Textbook content (Markdown)
│   │   ├── intro.md                   # Introduction
│   │   ├── chapter-01.md              # Chapter 1: Fundamentals
│   │   ├── chapter-02.md              # Chapter 2: Math Foundations
│   │   └── ...                        # Chapters 3-10
│   │
│   ├── src/                           # React source code
│   │   ├── components/                # React components
│   │   │   ├── ChatbotWidget.jsx      # Floating AI chatbot
│   │   │   ├── PersonalizeButton.jsx  # Personalization feature
│   │   │   ├── TranslateButton.jsx    # Translation feature
│   │   │   ├── DocPageActions.jsx     # Combined action buttons
│   │   │   └── AuthMenu.jsx           # Authentication UI
│   │   │
│   │   ├── pages/                     # Custom pages
│   │   │   └── index.js               # Homepage
│   │   │
│   │   ├── css/                       # Stylesheets
│   │   │   └── custom.css             # Global styles
│   │   │
│   │   └── theme/                     # Docusaurus theme overrides
│   │       └── Root.js                # App wrapper (includes ChatbotWidget)
│   │
│   ├── static/                        # Static assets
│   │   └── img/                       # Images, favicons
│   │
│   ├── docusaurus.config.js           # Docusaurus configuration
│   ├── sidebars.js                    # Sidebar structure
│   ├── package.json                   # Node dependencies
│   ├── package-lock.json              # Dependency lock file
│   ├── vercel.json                    # Vercel deployment config
│   ├── .vercelignore                  # Vercel ignore patterns
│   ├── .env.example                   # Environment variables template
│   └── README.md                      # Frontend documentation
│
├── backend/                            # BACKEND (FastAPI)
│   ├── server/                        # Main application code
│   │   ├── auth/                      # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # User database models
│   │   │   ├── routes.py              # Auth endpoints
│   │   │   └── security.py            # JWT, password hashing
│   │   │
│   │   ├── personalize/               # Personalization module
│   │   │   ├── __init__.py
│   │   │   ├── engine.py              # Personalization logic
│   │   │   ├── models.py              # Pydantic models
│   │   │   ├── routes.py              # Personalization endpoints
│   │   │   ├── cache_manager.py       # Caching system
│   │   │   └── transformer.py         # Content transformation
│   │   │
│   │   ├── translate/                 # Translation module
│   │   │   ├── __init__.py
│   │   │   ├── translator.py          # Urdu translation logic
│   │   │   ├── models.py              # Pydantic models
│   │   │   ├── routes.py              # Translation endpoints
│   │   │   ├── cache_manager.py       # Translation cache
│   │   │   └── glossary.json          # Technical term glossary
│   │   │
│   │   ├── rag/                       # RAG chatbot module
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # RAG endpoints
│   │   │   └── models.py              # Pydantic models
│   │   │
│   │   ├── agents/                    # AI Agents module
│   │   │   ├── __init__.py
│   │   │   ├── agent_base.py          # Base agent class
│   │   │   ├── code_explainer_agent.py # Code explanation
│   │   │   ├── quiz_generator_agent.py # Quiz generation
│   │   │   ├── summarizer_agent.py    # Content summarization
│   │   │   └── routes.py              # Agent endpoints
│   │   │
│   │   ├── tests/                     # Test suite
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py            # Pytest configuration
│   │   │   ├── test_auth.py           # Auth tests
│   │   │   ├── test_personalize.py    # Personalization tests
│   │   │   ├── test_translate.py      # Translation tests
│   │   │   ├── test_rag.py            # RAG tests
│   │   │   └── test_agents.py         # Agent tests
│   │   │
│   │   ├── migrations/                # Database migrations
│   │   │   ├── 001_add_personalization_cache.sql
│   │   │   └── 002_add_translation_content_hash.sql
│   │   │
│   │   └── __init__.py
│   │
│   ├── rag/                           # RAG engine (reusable)
│   │   ├── api/                       # RAG API implementation
│   │   │   ├── __init__.py
│   │   │   ├── main.py                # Legacy RAG server
│   │   │   ├── rag_engine.py          # Vector search engine
│   │   │   ├── openai_agent.py        # OpenAI integration
│   │   │   ├── gemini_agent.py        # Gemini integration
│   │   │   ├── database.py            # RAG database models
│   │   │   └── personalization_api.py # (Legacy)
│   │   │
│   │   ├── loaders/                   # Document loaders
│   │   │   ├── __init__.py
│   │   │   └── document_loader.py     # Markdown document loader
│   │   │
│   │   ├── utils/                     # Utilities
│   │   │   ├── __init__.py
│   │   │   └── text_splitter.py       # Text chunking
│   │   │
│   │   ├── embed_docs.py              # Document embedding script
│   │   └── requirements.txt           # RAG-specific dependencies
│   │
│   ├── personalization/               # Personalization engine (reusable)
│   │   ├── __init__.py
│   │   └── personalization_engine.py  # Core personalization logic
│   │
│   ├── agents/                        # Reusable AI agents
│   │   ├── __init__.py
│   │   ├── book_writer_agent.py       # Chapter writing agent
│   │   └── translation_agent.py       # Translation agent
│   │
│   ├── main.py                        # Main FastAPI app entry point
│   ├── requirements.txt               # Python dependencies
│   ├── railway.json                   # Railway deployment config
│   ├── .env.example                   # Environment variables template
│   └── README.md                      # Backend documentation
│
├── .github/                            # GitHub configuration
│   └── workflows/                     # GitHub Actions
│       ├── deploy.yml                 # Frontend deployment
│       ├── deploy-backend.yml         # Backend deployment
│       └── ci.yml                     # CI/CD pipeline
│
├── .gitignore                         # Git ignore patterns
├── LICENSE                            # MIT License
├── README.md                          # Main project documentation
├── DEPLOYMENT_GUIDE.md                # Deployment instructions
├── PROJECT_STRUCTURE.md               # This file
├── FIXES_APPLIED.md                   # Recent changes log
└── IMMEDIATE_DEPLOYMENT_STEPS.md      # Quick deployment guide
```

## File Counts

### Frontend
- **React Components:** 6 files
- **Markdown Chapters:** 11 files (intro + 10 chapters)
- **Configuration Files:** 3 files
- **Total Frontend Files:** ~25 files

### Backend
- **Python Modules:** 35+ files
- **Tests:** 6 test files
- **Configuration Files:** 4 files
- **Total Backend Files:** ~50 files

## Module Descriptions

### Frontend Modules

#### `/frontend/docs`
Markdown content for the textbook. Each chapter includes:
- Learning objectives
- Theory and explanations
- Code examples
- Practical tasks
- Checkpoint quizzes
- AI deep learning prompts

#### `/frontend/src/components`
Reusable React components:
- **ChatbotWidget:** Floating AI chatbot available on all pages
- **PersonalizeButton:** Triggers content personalization
- **TranslateButton:** Triggers Urdu translation
- **DocPageActions:** Wrapper component combining Personalize + Translate
- **AuthMenu:** User authentication interface

#### `/frontend/src/theme`
Docusaurus theme customization:
- **Root.js:** App wrapper that includes ChatbotWidget globally

### Backend Modules

#### `/backend/server/auth`
User authentication system:
- JWT token generation and validation
- Password hashing with bcrypt
- User signup/signin endpoints
- PostgreSQL user storage

#### `/backend/server/personalize`
Content personalization:
- Analyzes user profile (education, programming level)
- Adapts chapter content difficulty
- Caches personalized versions
- API endpoints for personalization

#### `/backend/server/translate`
Urdu translation system:
- OpenAI-based translation
- Technical term glossary
- Content hash-based caching
- Markdown format preservation

#### `/backend/server/rag`
RAG chatbot system:
- Vector search with Qdrant
- OpenAI/Gemini integration
- Context-aware responses
- Source attribution

#### `/backend/server/agents`
AI agent modules:
- Code explainer
- Quiz generator
- Content summarizer
- Extensible agent base class

#### `/backend/rag`
Reusable RAG engine:
- Document loading and chunking
- Vector embedding generation
- Semantic search functionality
- Can be used independently

#### `/backend/personalization`
Standalone personalization engine:
- Can be imported by other modules
- Configurable difficulty levels
- Content transformation logic

## Configuration Files

### Frontend

| File | Purpose |
|------|---------|
| `docusaurus.config.js` | Main Docusaurus configuration |
| `sidebars.js` | Sidebar navigation structure |
| `vercel.json` | Vercel deployment settings |
| `package.json` | Node.js dependencies |
| `.env.example` | Environment variables template |

### Backend

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point |
| `requirements.txt` | Python dependencies |
| `railway.json` | Railway deployment settings |
| `.env.example` | Environment variables template |

## Dependencies

### Frontend Dependencies (Node.js)

**Core:**
- `@docusaurus/core` ^3.1.0
- `react` ^18.2.0
- `react-dom` ^18.2.0

**Utilities:**
- `axios` ^1.13.2 (HTTP client)
- `clsx` ^2.0.0 (CSS utility)

**Total:** ~8 direct dependencies

### Backend Dependencies (Python)

**Framework:**
- `fastapi` 0.109.0
- `uvicorn` 0.27.0

**AI/ML:**
- `openai` 1.12.0
- `google-generativeai` 0.3.2
- `anthropic` 0.8.1
- `langchain` 0.1.6

**Database:**
- `sqlalchemy` 2.0.25
- `psycopg2-binary` 2.9.9
- `qdrant-client` 1.7.1

**Total:** ~35 direct dependencies

## Data Flow

### RAG Chatbot Flow

```
User types question
    ↓
Frontend (ChatbotWidget.jsx)
    ↓
Backend API (/api/rag/ask)
    ↓
RAG Engine (rag_engine.py)
    ↓
Qdrant (vector search)
    ↓
OpenAI (generate response)
    ↓
Response with sources
    ↓
Display in chatbot UI
```

### Personalization Flow

```
User clicks "Personalize"
    ↓
Frontend (PersonalizeButton.jsx)
    ↓
Backend API (/api/personalize)
    ↓
Fetch user profile
    ↓
Personalization Engine
    ↓
OpenAI (rewrite content)
    ↓
Cache result
    ↓
Return personalized chapter
    ↓
Display in frontend
```

## Environment Variables

### Frontend

```env
REACT_APP_API_URL=http://localhost:8000
```

### Backend

```env
# Database
DATABASE_URL=sqlite:///./physical_ai.db

# AI Keys
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Vector DB
QDRANT_URL=https://...
QDRANT_API_KEY=...

# Auth
JWT_SECRET=...

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment

### Frontend → Vercel
- Root directory: `frontend/`
- Build command: `npm run build`
- Output: `frontend/build/`

### Backend → Railway
- Root directory: `backend/`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Testing

### Frontend Tests
Location: `frontend/src/components/__tests__/`
Run: `cd frontend && npm test`

### Backend Tests
Location: `backend/server/tests/`
Run: `cd backend && pytest`

## Development Tips

1. **Frontend only:** `cd frontend && npm start`
2. **Backend only:** `cd backend && uvicorn main:app --reload`
3. **Full stack:** Run both in separate terminals
4. **Hot reload:** Both support auto-reload on file changes

---

**Last Updated:** 2025-12-18
**Structure Version:** 2.0.0 (Refactored)
