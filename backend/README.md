# Physical AI Textbook - Backend

FastAPI backend server providing authentication, RAG chatbot, personalization, and translation services.

## Features

- 🔐 **Authentication** - User signup/signin with JWT
- 🤖 **RAG Chatbot** - AI-powered Q&A with document search
- ✨ **Personalization** - Adaptive content based on user level
- 🌐 **Translation** - Urdu translation with technical glossary
- 🎯 **AI Agents** - Code explainer, quiz generator, summarizer

## Tech Stack

- **Framework:** FastAPI 0.109
- **Database:** PostgreSQL (Neon) / SQLite (local)
- **Vector DB:** Qdrant Cloud
- **AI:** OpenAI GPT-4, Google Gemini, Claude
- **Auth:** JWT with bcrypt

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run Development Server

```bash
uvicorn main:app --reload
```

Server runs at: `http://localhost:8000`

API docs at: `http://localhost:8000/docs`

## Project Structure

```
backend/
├── main.py                 # Main FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
│
├── server/                # Main application code
│   ├── auth/             # Authentication & JWT
│   ├── personalize/      # Content personalization
│   ├── translate/        # Urdu translation
│   ├── rag/              # RAG chatbot routes
│   ├── agents/           # AI agents (quiz, explain, etc.)
│   ├── tests/            # Test suite
│   └── main.py           # (Legacy - use ../main.py instead)
│
├── rag/                   # RAG engine & embeddings
│   ├── api/              # RAG API implementation
│   ├── loaders/          # Document loaders
│   └── utils/            # Text splitting utilities
│
├── personalization/       # Personalization engine
│   └── personalization_engine.py
│
└── agents/               # Reusable AI agents
    ├── book_writer_agent.py
    └── translation_agent.py
```

## API Endpoints

### Core Routes

- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- `GET /` - API information

### Authentication (`/auth`)

- `POST /auth/signup` - Create new user
- `POST /auth/signin` - Login
- `GET /auth/me` - Get current user

### RAG Chatbot (`/api/rag`)

- `POST /api/rag/ask` - Ask question with AI response
- `POST /api/rag/search` - Semantic search
- `POST /api/rag/embed` - Embed documents
- `GET /api/rag/history/{user_id}` - Chat history

### Personalization (`/api`)

- `POST /api/personalize` - Personalize chapter content
- `POST /api/update-profile` - Update user profile
- `GET /api/profile/{user_id}` - Get user profile

### Translation (`/api`)

- `POST /api/translate` - Translate to Urdu
- `GET /api/translate/glossary` - Get technical glossary

### AI Agents (`/api/agent`)

- `POST /api/agent/explain` - Explain code
- `POST /api/agent/quiz` - Generate quiz
- `POST /api/agent/summarize` - Summarize content

## Environment Variables

Required variables (see `.env.example` for all options):

```env
# Database
DATABASE_URL=sqlite:///./physical_ai.db

# AI Keys (at least one required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Vector DB (for RAG)
QDRANT_URL=https://...
QDRANT_API_KEY=...

# Auth
JWT_SECRET=your-secret-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Deployment

### Railway (Recommended)

1. **Create Railway project:**
   ```bash
   railway init
   railway link
   ```

2. **Add environment variables:**
   ```bash
   railway variables set DATABASE_URL=...
   railway variables set OPENAI_API_KEY=...
   railway variables set ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

Configuration in `railway.json` is already set.

### Render

1. Create new Web Service
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard

### Docker

```bash
docker build -t physical-ai-backend .
docker run -p 8000:8000 --env-file .env physical-ai-backend
```

## Testing

Run tests:

```bash
cd backend
pytest
```

With coverage:

```bash
pytest --cov=server --cov-report=html
```

## Development

### Adding a New Route

1. Create route file in appropriate module (e.g., `server/new_feature/routes.py`)
2. Define Pydantic models in `models.py`
3. Import and mount router in `main.py`

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Common Issues

### Issue: Import errors

**Solution:** Make sure you're running from `backend/` directory:
```bash
cd backend
python -m uvicorn main:app --reload
```

### Issue: CORS errors

**Solution:** Update `ALLOWED_ORIGINS` in `.env` to include your frontend URL:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

### Issue: Database connection failed

**Solution:** Check `DATABASE_URL` format. For Neon:
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

## Contributing

1. Create feature branch
2. Make changes
3. Add tests
4. Run test suite
5. Submit PR

## License

MIT License - see LICENSE file

## Support

- Documentation: `/docs` endpoint
- Issues: GitHub Issues
- Health check: `GET /health`

---

**Happy coding!** 🚀
