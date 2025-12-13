# Deployment Guide - Physical AI Textbook

**Last Updated:** 2025-12-14
**Version:** 2.0.0

---

## 🚀 Deployment Architecture

### Recommended Setup

```
┌─────────────────────────────────────────┐
│          User's Browser                 │
└────────────┬────────────────────────────┘
             │
             ├─────────────┐
             │             │
    ┌────────▼──────┐  ┌──▼──────────────┐
    │  Vercel       │  │  Railway/Render │
    │  (Frontend)   │  │  (Backend)      │
    │               │  │                 │
    │  Docusaurus   │  │  FastAPI        │
    │  React        │  │  Python 3.11    │
    └───────────────┘  └─────────┬───────┘
                                 │
                     ┌───────────┴─────────────┐
                     │                         │
              ┌──────▼──────┐           ┌──────▼──────┐
              │  Neon       │           │  Qdrant     │
              │  (Postgres) │           │  (Vectors)  │
              └─────────────┘           └─────────────┘
```

**Services:**
- **Frontend:** Vercel (or GitHub Pages)
- **Backend:** Railway (or Render)
- **Database:** Neon Serverless Postgres
- **Vector DB:** Qdrant Cloud
- **LLM:** Claude API / OpenAI API

---

## 📋 Prerequisites

### Required Accounts

1. **GitHub** - Source code hosting
2. **Vercel** - Frontend deployment (free tier)
3. **Railway** - Backend deployment (free tier: $5 credit/month)
4. **Neon** - Serverless Postgres (free tier: 1 project)
5. **Qdrant Cloud** - Vector database (free tier: 1GB)
6. **Anthropic** - Claude API (pay-as-you-go)
7. **OpenAI** - GPT API (pay-as-you-go, optional)

---

## 🔧 Step 1: Setup Third-Party Services

### 1.1 Neon Postgres Database

1. Sign up at https://neon.tech
2. Create new project: "physical-ai-textbook"
3. Copy connection string:
   ```
   postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
   ```
4. Save as `DATABASE_URL`

### 1.2 Qdrant Vector Database

1. Sign up at https://cloud.qdrant.io
2. Create cluster: "physical-ai-rag"
3. Get API credentials:
   - URL: `https://xxx.qdrant.io:6333`
   - API Key: `your-api-key`
4. Save as `QDRANT_URL` and `QDRANT_API_KEY`

### 1.3 Claude API

1. Sign up at https://console.anthropic.com
2. Generate API key
3. Save as `CLAUDE_API_KEY`

### 1.4 OpenAI API (Optional)

1. Sign up at https://platform.openai.com
2. Generate API key
3. Save as `OPENAI_API_KEY`

---

## 🖥️ Step 2: Deploy Backend to Railway

### Option A: Using Railway CLI (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to GitHub repo
railway link

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set CLAUDE_API_KEY="sk-ant-..."
railway variables set OPENAI_API_KEY="sk-..."
railway variables set QDRANT_URL="https://..."
railway variables set QDRANT_API_KEY="..."
railway variables set JWT_SECRET="your-secret-key-here"
railway variables set LLM_PROVIDER="claude"

# Deploy
railway up
```

### Option B: Using Railway Dashboard

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Configure:
   - **Root Directory:** `server`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see above)
6. Deploy

### Verify Backend Deployment

```bash
# Check health endpoint
curl https://your-railway-app.railway.app/health

# Check API docs
open https://your-railway-app.railway.app/docs
```

---

## 🌐 Step 3: Deploy Frontend to Vercel

### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variable
vercel env add REACT_APP_API_URL production
# Enter: https://your-railway-app.railway.app

# Deploy to production
vercel --prod
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Docusaurus
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
5. Add environment variables:
   - `REACT_APP_API_URL` = `https://your-railway-app.railway.app`
6. Deploy

### Verify Frontend Deployment

```bash
# Open in browser
open https://your-project.vercel.app
```

---

## 📊 Step 4: Run Database Migrations

```bash
# SSH into Railway container (or run locally with production DATABASE_URL)
cd server

python -c "
from auth.database import engine, init_db
from sqlalchemy import text
import glob

# Create tables
init_db()

# Run migrations
migration_files = sorted(glob.glob('migrations/*.sql'))
for migration_file in migration_files:
    print(f'Running migration: {migration_file}')
    with open(migration_file) as f:
        sql = f.read()
    with engine.connect() as conn:
        for statement in sql.split(';'):
            if statement.strip():
                conn.execute(text(statement))
        conn.commit()

print('✅ Migrations completed')
"
```

---

## 🤖 Step 5: Populate Vector Database (RAG)

```bash
cd rag

# Set environment variables
export QDRANT_URL="https://..."
export QDRANT_API_KEY="..."
export OPENAI_API_KEY="sk-..."

# Run embedding script
python embed_docs.py

# Verify
# You should see:
# Processing 100+ chunks from 10 documents
# ✅ Embedding Complete
```

---

## 🔐 Step 6: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

### Backend (Railway)
- `RAILWAY_TOKEN` - From https://railway.app/account/tokens
- `RAILWAY_PROJECT_ID` - From Railway dashboard
- `RAILWAY_URL` - Your Railway app URL

### Frontend (Vercel)
- `VERCEL_TOKEN` - From https://vercel.com/account/tokens
- `VERCEL_ORG_ID` - From Vercel dashboard
- `VERCEL_PROJECT_ID` - From Vercel dashboard

### Database & APIs
- `DATABASE_URL` - Neon connection string
- `QDRANT_URL` - Qdrant cluster URL
- `QDRANT_API_KEY` - Qdrant API key
- `CLAUDE_API_KEY` - Anthropic API key
- `OPENAI_API_KEY` - OpenAI API key
- `JWT_SECRET` - Random secret key (generate with `openssl rand -hex 32`)

### URLs
- `BACKEND_URL` - Railway app URL
- `FRONTEND_URL` - Vercel app URL

---

## ✅ Step 7: Verify Deployment

### Backend Health Checks

```bash
BACKEND_URL="https://your-railway-app.railway.app"

# Overall health
curl $BACKEND_URL/health

# API documentation
open $BACKEND_URL/docs

# Module health checks
curl $BACKEND_URL/api/personalize/health
curl $BACKEND_URL/api/translate/health
curl $BACKEND_URL/api/rag/health
```

### Frontend Verification

1. Open https://your-project.vercel.app
2. Navigate to a chapter
3. Test features:
   - ✅ Sign up / Login
   - ✅ Personalize chapter
   - ✅ Translate to Urdu
   - ✅ Chat with AI (if RAG enabled)

---

## 🔄 Step 8: Setup CI/CD (Automated)

CI/CD is already configured via GitHub Actions!

### Workflows

1. **`.github/workflows/ci.yml`** - Runs on every push/PR
   - Backend tests (Python)
   - Frontend tests (Node.js)
   - Security scanning
   - Docker build
   - Code quality checks

2. **`.github/workflows/deploy-backend.yml`** - Deploys backend on push to `main`
   - Deploys to Railway
   - Runs migrations
   - Health checks

3. **`.github/workflows/deploy.yml`** - Deploys frontend to GitHub Pages

### Trigger Deployments

```bash
# Push to main branch triggers automatic deployment
git push origin main

# Or manually trigger via GitHub Actions UI
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Problem:** Railway deployment fails

**Solutions:**
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Check Python version (must be 3.10 or 3.11)
4. Verify `requirements.txt` has all dependencies

```bash
# Test locally first
cd server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Database Connection Fails

**Problem:** `connection to server failed`

**Solutions:**
1. Check `DATABASE_URL` format (must include `?sslmode=require` for Neon)
2. Verify IP allowlist in Neon (set to `0.0.0.0/0` for Railway)
3. Test connection:

```bash
psql "postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require"
```

### LLM API Errors

**Problem:** `Anthropic API error: 401 Unauthorized`

**Solutions:**
1. Verify API key is correct
2. Check API key has sufficient credits
3. Test API key:

```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]}'
```

### Frontend API Calls Fail

**Problem:** CORS errors or 404 on `/api/*`

**Solutions:**
1. Verify `REACT_APP_API_URL` is set correctly in Vercel
2. Check CORS settings in `server/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-project.vercel.app"],  # Add your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Redeploy backend after changing CORS

---

## 📊 Monitoring & Logs

### Railway Logs

```bash
# View live logs
railway logs

# Or in dashboard: https://railway.app → Your Project → Deployments → Logs
```

### Vercel Logs

```bash
# View logs
vercel logs

# Or in dashboard: https://vercel.com → Your Project → Deployments → Logs
```

### Database Monitoring

- Neon: https://console.neon.tech → Monitoring
- Qdrant: https://cloud.qdrant.io → Clusters → Metrics

---

## 💰 Cost Estimate

### Free Tier Limits

| Service | Free Tier | Estimated Usage | Cost |
|---------|-----------|-----------------|------|
| **Vercel** | 100GB bandwidth/month | ~10GB | $0 |
| **Railway** | $5 credit/month | ~$3-4/month | $0 |
| **Neon** | 1 project, 3GB storage | ~500MB | $0 |
| **Qdrant** | 1GB vector storage | ~200MB | $0 |
| **Claude API** | Pay-as-you-go | ~1000 requests/month | ~$5-10 |
| **OpenAI API** | Pay-as-you-go | Fallback only | ~$2-5 |

**Total Estimated Cost:** $7-15/month (mostly LLM API usage)

### Cost Optimization Tips

1. **Use Caching Aggressively**
   - Translation cache hit rate >70% = 70% cost savings
   - Personalization cache hit rate >60%

2. **Implement Rate Limiting**
   - Limit users to 20 translations/hour
   - Limit chat to 50 messages/day

3. **Use Cheaper Models for Simple Tasks**
   - Haiku for simple queries
   - Sonnet for complex transformations

4. **Monitor API Usage**
   - Set budget alerts in Anthropic/OpenAI dashboards
   - Track usage in database logs

---

## 🔒 Security Checklist

- [ ] All secrets stored in environment variables (never in code)
- [ ] JWT secret is strong (32+ random characters)
- [ ] Database uses SSL (`?sslmode=require`)
- [ ] API keys have appropriate permissions only
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled on backend
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using parameterized queries)
- [ ] HTTPS enforced (handled by Vercel/Railway)
- [ ] Security headers configured (X-Frame-Options, etc.)

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Neon Docs:** https://neon.tech/docs
- **Qdrant Docs:** https://qdrant.tech/documentation
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment
- **Docusaurus Deployment:** https://docusaurus.io/docs/deployment

---

## 🎯 Next Steps

After deployment:

1. **Test all features end-to-end**
2. **Monitor logs for errors**
3. **Set up budget alerts**
4. **Create demo video (Step H)**
5. **Prepare submission package (Step I)**

---

**Deployment Complete!** 🎉

Your Physical AI Textbook is now live and accessible worldwide!

- 🌐 **Frontend:** https://your-project.vercel.app
- 🔗 **API:** https://your-railway-app.railway.app
- 📚 **API Docs:** https://your-railway-app.railway.app/docs
