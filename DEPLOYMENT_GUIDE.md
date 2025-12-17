# Complete Deployment Guide - Physical AI Textbook

**For Beginners - Step by Step**

This guide will walk you through deploying your AI-powered Physical AI & Humanoid Robotics textbook from scratch. No prior deployment experience required!

---

## Table of Contents

1. [What is This Project?](#what-is-this-project)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Getting API Keys (Critical Step)](#getting-api-keys)
5. [Local Development Setup](#local-development-setup)
6. [Deploying to Production](#deploying-to-production)
7. [Common Errors & Solutions](#common-errors--solutions)
8. [Security Best Practices](#security-best-practices)
9. [Cost Breakdown](#cost-breakdown)

---

## What is This Project?

This is an **AI-native interactive textbook** about Physical AI and Humanoid Robotics with these features:

- 📚 **10 Comprehensive Chapters** - Complete learning material
- 🤖 **RAG Chatbot** - Ask questions about any chapter
- ✨ **Personalization** - Content adapts to your skill level
- 🌐 **Urdu Translation** - Multilingual support
- 💬 **Smart UI** - Highlight text and ask questions

**Technology Stack:**
- Frontend: Docusaurus (React-based static site)
- Backend: FastAPI (Python web framework)
- Database: PostgreSQL (user data, chat history)
- Vector Database: Qdrant (for AI search)
- AI: OpenAI GPT-4 or Google Gemini

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              USER'S BROWSER                     │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    ┌────▼─────┐      ┌─────▼──────┐
    │ FRONTEND │      │  BACKEND   │
    │ (Vercel/ │      │ (Railway/  │
    │  GitHub  │      │  Render)   │
    │  Pages)  │      │            │
    └──────────┘      └──────┬─────┘
                             │
                   ┌─────────┴──────────┐
                   │                    │
            ┌──────▼─────┐     ┌───────▼────────┐
            │ PostgreSQL │     │ Qdrant Vector  │
            │  Database  │     │    Database    │
            │   (Neon)   │     │   (Qdrant.io)  │
            └────────────┘     └────────────────┘
```

### Important Note: Dual Backend Architecture

This project has **TWO separate backends** (historical artifact from development):

1. **`/rag/api/main.py`** - Simple RAG chatbot backend (older, simpler)
2. **`/server/main.py`** - Full-featured backend (newer, recommended)

**For deployment, you should use `/server/main.py`** as it includes:
- Authentication
- Personalization
- Translation
- RAG chatbot
- All features integrated

---

## Prerequisites

### Software Requirements

Before starting, install these on your computer:

| Software | Version | Download Link | Why You Need It |
|----------|---------|---------------|-----------------|
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) | Runs the frontend |
| **Python** | 3.9+ | [python.org](https://www.python.org/) | Runs the backend |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) | Version control |
| **Text Editor** | Any | [VSCode](https://code.visualstudio.com/) (recommended) | Edit code |

### Cloud Accounts Needed (All FREE Tiers Available)

| Service | Purpose | Free Tier | Sign Up Link |
|---------|---------|-----------|--------------|
| **GitHub** | Code hosting | ✅ Unlimited public repos | [github.com](https://github.com/signup) |
| **Vercel** | Frontend hosting | ✅ 100GB bandwidth/month | [vercel.com](https://vercel.com/signup) |
| **Railway** | Backend hosting | ✅ $5 free credit/month | [railway.app](https://railway.app/) |
| **Neon** | PostgreSQL database | ✅ 1 free project | [neon.tech](https://neon.tech/) |
| **Qdrant Cloud** | Vector database | ✅ 1GB storage | [cloud.qdrant.io](https://cloud.qdrant.io/) |
| **OpenAI** or **Google** | AI provider | ⚠️ Pay-as-you-go | [platform.openai.com](https://platform.openai.com/) |

---

## Getting API Keys

### ⚠️ CRITICAL SECURITY WARNING

**NEVER, EVER:**
- ❌ Commit API keys to Git
- ❌ Share API keys publicly
- ❌ Hardcode keys in your code
- ❌ Post keys in screenshots or videos

**ALWAYS:**
- ✅ Store keys in `.env` files (which are `.gitignore`d)
- ✅ Use environment variables in deployment platforms
- ✅ Rotate keys if accidentally exposed
- ✅ Set spending limits on API accounts

---

### Option 1: OpenAI API Key (Recommended, More Features)

**What you get:** GPT-4, embeddings, full RAG chatbot, personalization, translation

**Cost:** ~$0.50-2.00 per day for moderate testing (you control spending limits)

**Steps:**

1. **Go to** [platform.openai.com](https://platform.openai.com/)
2. **Sign up** or log in
3. **Click** your profile → "View API keys"
4. **Click** "Create new secret key"
5. **Name it** something like "physical-ai-textbook"
6. **Copy the key** (starts with `sk-...`) - **You'll only see this once!**
7. **Save it** somewhere safe temporarily (we'll add it to `.env` later)
8. **Add credits:**
   - Click "Settings" → "Billing"
   - Add $10-20 to start
   - Set a **spending limit** (e.g., $5/month) to avoid surprises

**What it costs:**
- Embeddings: ~$0.10 per 1000 pages
- GPT-4 queries: ~$0.01-0.03 per question
- **Total for testing:** $5-10 should last weeks

---

### Option 2: Google Gemini API Key (Free Tier, Limited Features)

**What you get:** Basic chatbot (no full RAG, limited personalization)

**Cost:** FREE up to 60 requests/minute

**Steps:**

1. **Go to** [ai.google.dev](https://ai.google.dev/)
2. **Click** "Get API key in Google AI Studio"
3. **Sign in** with Google account
4. **Click** "Create API Key"
5. **Copy the key** - Save it safely
6. **Note:** Free tier has rate limits (60 requests/min)

**Limitations:**
- No embeddings → No semantic search
- Simpler chatbot (no document context)
- Good for: Testing the UI and basic functionality

---

### Database Setup

#### 1. Neon PostgreSQL (FREE)

**Why:** Stores user profiles, chat history, personalization cache

**Steps:**

1. **Go to** [neon.tech](https://neon.tech/)
2. **Sign up** with GitHub (easiest)
3. **Create new project:**
   - Name: `physical-ai-textbook`
   - Region: Choose closest to you
4. **Get connection string:**
   - Click "Connection Details"
   - Copy the string that looks like:
     ```
     postgresql://username:password@ep-xyz-123.us-east-2.aws.neon.tech/neondb?sslmode=require
     ```
5. **Save it** - We'll add it to `.env` as `DATABASE_URL`

**Important:** The free tier includes 1 project with 0.5GB storage (plenty for this project).

---

#### 2. Qdrant Vector Database (FREE)

**Why:** Stores document embeddings for semantic search (RAG chatbot)

**Steps:**

1. **Go to** [cloud.qdrant.io](https://cloud.qdrant.io/)
2. **Sign up** (email or GitHub)
3. **Create cluster:**
   - Name: `physical-ai-rag`
   - Region: Choose closest to you
   - Plan: Free tier (1GB)
4. **Get credentials:**
   - Click on your cluster
   - Copy **Cluster URL** (looks like `https://xyz-abc.qdrant.io`)
   - Click "API Keys" → Copy the API key
5. **Save both** - We'll add them to `.env`

---

## Local Development Setup

### Step 1: Clone the Repository

```bash
# Open terminal/command prompt
cd Desktop  # or wherever you want the project

# Clone the repo (replace with your fork if you made one)
git clone https://github.com/your-username/physical-AI.git
cd physical-AI
```

---

### Step 2: Install Frontend Dependencies

```bash
# Make sure you're in the project root
npm install
```

**This installs:** Docusaurus, React, and all frontend packages.

**Expected output:**
```
added 1234 packages in 45s
```

**If errors occur:**
- Make sure Node.js 18+ is installed: `node --version`
- Delete `node_modules` and `package-lock.json`, then try again

---

### Step 3: Install Backend Dependencies

```bash
# Navigate to server directory
cd server

# Install Python packages
pip install -r requirements.txt

# Go back to project root
cd ..
```

**This installs:** FastAPI, OpenAI SDK, database drivers, etc.

**Expected output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 ...
```

**If errors occur:**
- Make sure Python 3.9+ is installed: `python --version`
- On Windows, try `python -m pip install -r requirements.txt`
- On Mac/Linux, you might need `pip3` instead of `pip`

---

### Step 4: Create Environment File

```bash
# Copy the example file
cp server/.env.example server/.env

# Open server/.env in your text editor
```

**Edit `server/.env` and add your API keys:**

```env
# ==================== DATABASE ====================
# Use SQLite for local development (no setup needed)
DATABASE_URL=sqlite:///./physical_ai.db

# For production, use your Neon connection string:
# DATABASE_URL=postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require

# ==================== AUTHENTICATION ====================
JWT_SECRET=change-this-to-a-random-string-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# ==================== LLM API KEYS ====================
# Option 1: OpenAI (Recommended - Full features)
OPENAI_API_KEY=sk-your-openai-key-here

# Option 2: Google Gemini (Free tier - Basic features)
# GEMINI_API_KEY=your-gemini-key-here

# ==================== VECTOR DATABASE ====================
# Qdrant Cloud credentials (from earlier setup)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# ==================== FEATURE FLAGS ====================
DEMO_MODE=false
FEATURE_TRANSLATION=true
FEATURE_PERSONALIZATION=true
FEATURE_RAG_CHAT=true

# ==================== CORS ====================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Security reminder:**
- The `server/.env` file is already in `.gitignore`
- Never commit this file to Git
- Keep your API keys secret!

---

### Step 5: Initialize the Database

```bash
cd server
python -c "from auth.database import init_db; init_db()"
cd ..
```

**This creates:** Database tables for users, chat history, and cache.

**Expected output:**
```
Database initialized successfully
Created tables: users, chat_history, personalization_cache
```

---

### Step 6: Run the Project Locally

You need **TWO terminal windows** open:

**Terminal 1 - Backend:**
```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this running!**

---

**Terminal 2 - Frontend:**
```bash
# From project root
npm start
```

**Expected output:**
```
Starting development server...
Docusaurus website running at http://localhost:3000
```

---

### Step 7: Test Locally

1. **Open browser:** [http://localhost:3000](http://localhost:3000)
2. **You should see:** The homepage with hero section
3. **Navigate to:** "Start Reading" → Any chapter
4. **Test chatbot:** Look for the 💬 floating button (bottom-right)
5. **Click it** and ask: "What is Physical AI?"
6. **You should get** an AI-powered response

**If chatbot doesn't work:**
- Check backend is running (terminal 1 should show no errors)
- Check browser console (F12) for errors
- Verify API keys are correctly set in `.env`

---

## Deploying to Production

Now that it works locally, let's deploy it to the internet!

---

### Part 1: Deploy Frontend to Vercel

**Why Vercel?** It's the easiest way to deploy Docusaurus sites. Free tier is generous.

**Steps:**

1. **Push code to GitHub** (if you haven't already):
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Go to** [vercel.com](https://vercel.com/)

3. **Sign in** with GitHub

4. **Click** "Add New Project"

5. **Import** your `physical-AI` repository

6. **Configure:**
   - Framework Preset: **Docusaurus**
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Root Directory: `./` (leave default)

7. **Environment Variables:**
   - Click "Environment Variables"
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.railway.app`
   - (You'll get this URL in the next step - you can add it later)

8. **Click** "Deploy"

9. **Wait** 2-3 minutes for build to complete

10. **Get your URL:** Something like `https://physical-ai-abc123.vercel.app`

**Note:** Don't worry if the chatbot doesn't work yet - we haven't deployed the backend!

---

### Part 2: Deploy Backend to Railway

**Why Railway?** Offers $5 free credit/month, supports Python, easy PostgreSQL setup.

**Steps:**

1. **Go to** [railway.app](https://railway.app/)

2. **Sign in** with GitHub

3. **Click** "New Project"

4. **Select** "Deploy from GitHub repo"

5. **Choose** your `physical-AI` repository

6. **Configure:**
   - Click "Add Service" → "GitHub Repo"
   - Root Directory: `server`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

7. **Add Environment Variables:**
   Click "Variables" tab and add ALL of these:

   ```env
   DATABASE_URL=<your-neon-connection-string>
   OPENAI_API_KEY=<your-openai-key>
   QDRANT_URL=<your-qdrant-url>
   QDRANT_API_KEY=<your-qdrant-key>
   JWT_SECRET=<generate-random-string>
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app,http://localhost:3000
   DEMO_MODE=false
   FEATURE_TRANSLATION=true
   FEATURE_PERSONALIZATION=true
   FEATURE_RAG_CHAT=true
   PORT=8000
   ```

8. **Generate JWT_SECRET:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Copy the output and paste as `JWT_SECRET`

9. **Click** "Deploy"

10. **Get your backend URL:**
    - Click "Settings" → "Networking"
    - Copy the public URL (e.g., `https://physical-ai-production.up.railway.app`)

11. **Go back to Vercel:**
    - Open your Vercel project
    - Settings → Environment Variables
    - Edit `REACT_APP_API_URL` to your Railway URL
    - Click "Redeploy"

---

### Part 3: Update CORS Settings

Now that you have both URLs, update the backend CORS settings:

1. **In Railway:**
   - Go to Variables
   - Update `ALLOWED_ORIGINS` to include your Vercel URL:
     ```
     https://your-app.vercel.app,http://localhost:3000
     ```
   - Click "Save" and redeploy

---

### Part 4: Embed Documents (One-Time Setup)

Your chatbot needs to know about your textbook content. Let's embed it:

**Option 1: Using Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run embedding script
railway run python -c "from rag.routes import embed_all_documents; import asyncio; asyncio.run(embed_all_documents('../docs'))"
```

**Option 2: Using API Endpoint**

```bash
curl -X POST https://your-backend.railway.app/api/rag/embed \
  -H "Content-Type: application/json" \
  -d '{"docs_path": "./docs"}'
```

**This will:**
- Load all 10 chapters
- Split them into chunks
- Create embeddings using OpenAI
- Store in Qdrant

**Expected time:** 2-5 minutes
**Cost:** ~$0.50-1.00 (one-time)

---

### Part 5: Test Production Deployment

1. **Visit** your Vercel URL: `https://your-app.vercel.app`
2. **Navigate** to any chapter
3. **Click** the 💬 chatbot button
4. **Ask** a question
5. **Verify** you get a response with sources

**Success checklist:**
- ✅ Homepage loads
- ✅ Chapters are readable
- ✅ Chatbot button appears
- ✅ Chatbot responds to questions
- ✅ Sources are cited

---

## Common Errors & Solutions

### Frontend Errors

#### Error: "Failed to fetch" when using chatbot

**Cause:** Backend not running or CORS misconfigured

**Solution:**
1. Check backend is running: Visit `https://your-backend.railway.app/health`
2. Should return: `{"status": "ok"}`
3. If not, check Railway logs for errors
4. Verify `ALLOWED_ORIGINS` includes your Vercel URL

---

#### Error: "Module not found"

**Cause:** Dependencies not installed

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

---

### Backend Errors

#### Error: "Connection refused" to Qdrant

**Cause:** Wrong Qdrant URL or API key

**Solution:**
1. Go to Qdrant Cloud dashboard
2. Verify cluster is running (not paused)
3. Copy URL again - make sure it's HTTPS
4. Regenerate API key if needed
5. Update environment variables in Railway

---

#### Error: "Invalid API key" for OpenAI

**Cause:** Wrong key or insufficient credits

**Solution:**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Verify key is active
3. Check billing: Settings → Billing → Add credits
4. Regenerate key if needed
5. Update environment variable in Railway

---

#### Error: "Database connection failed"

**Cause:** Wrong connection string or database not active

**Solution:**
1. Go to Neon dashboard
2. Verify project is active
3. Copy connection string again
4. Make sure it ends with `?sslmode=require`
5. Update `DATABASE_URL` in Railway

---

### Deployment Errors

#### Railway: "Build failed"

**Cause:** Wrong Python version or missing files

**Solution:**
1. Check Railway logs for specific error
2. Verify `server/requirements.txt` exists
3. Make sure Python 3.9+ is specified (Railway auto-detects)
4. Check start command is correct

---

#### Vercel: "Build failed"

**Cause:** Node version or build configuration

**Solution:**
1. Check build logs in Vercel dashboard
2. Verify Node.js 18+ is used
3. Make sure `package.json` has correct scripts
4. Try rebuilding: Deployments → "..." → Redeploy

---

## Security Best Practices

### Before Deploying to Production

**DO THIS CHECKLIST:**

- [ ] Change `JWT_SECRET` to a strong random string (32+ characters)
- [ ] Set `ALLOWED_ORIGINS` to only your Vercel domain (remove localhost)
- [ ] Enable spending limits on OpenAI account (e.g., $5/month)
- [ ] Never commit `.env` files to Git
- [ ] Use different API keys for development vs. production
- [ ] Enable MFA (multi-factor auth) on all cloud accounts
- [ ] Set up database backups in Neon (Settings → Backups)
- [ ] Review Qdrant access logs monthly

### API Key Rotation Schedule

**Every 3 months:**
- Rotate OpenAI API key
- Rotate Qdrant API key
- Rotate JWT_SECRET

**If leaked:**
- Immediately revoke exposed key
- Generate new key
- Update environment variables
- Check billing for unauthorized usage

---

## Cost Breakdown

### Monthly Costs (Low Usage)

| Service | Plan | Cost | Notes |
|---------|------|------|-------|
| **Vercel** | Free | $0 | Up to 100GB bandwidth |
| **Railway** | Hobby | $5 | $5 free credit/month |
| **Neon** | Free | $0 | 1 project, 0.5GB storage |
| **Qdrant** | Free | $0 | 1GB vector storage |
| **OpenAI** | Pay-as-you-go | $5-15 | Depends on usage |
| **Domain (optional)** | Namecheap | $10/year | Not required |
| **TOTAL** | | **$5-15/month** | |

### How to Reduce Costs

1. **Use Gemini instead of OpenAI:** FREE (but limited features)
2. **Enable caching:** Reduces duplicate API calls
3. **Set rate limits:** Prevent abuse
4. **Use Railway hobby plan wisely:** $5 credit renews monthly
5. **Monitor usage:** Check dashboards weekly

### Scaling Costs (High Usage)

**If you get 1000+ users:**

| Service | Upgrade | Cost |
|---------|---------|------|
| Vercel | Pro | $20/month |
| Railway | Pro | $20/month |
| Neon | Pro | $19/month |
| Qdrant | Standard | $25/month |
| OpenAI | Batch API | $50-200/month |
| **TOTAL** | | **$134-284/month** |

---

## Advanced Topics

### Custom Domain Setup

1. Buy domain from Namecheap/GoDaddy
2. In Vercel: Settings → Domains → Add
3. Follow DNS configuration instructions
4. Update `ALLOWED_ORIGINS` to include new domain

### CI/CD Pipeline

The project includes GitHub Actions:

- `.github/workflows/deploy.yml` - Auto-deploy on push to main
- Runs tests before deployment
- Vercel auto-deploys on push

### Monitoring & Analytics

**Recommended tools:**

- **Sentry:** Error tracking (free tier)
- **Vercel Analytics:** Page views (included)
- **OpenAI Usage Dashboard:** API costs
- **Railway Metrics:** Backend performance

---

## Getting Help

### Where to Ask Questions

1. **GitHub Issues:** [github.com/your-repo/issues](https://github.com)
2. **Docusaurus Discord:** [discord.gg/docusaurus](https://discord.gg/docusaurus)
3. **FastAPI Discord:** [discord.gg/fastapi](https://discord.gg/fastapi)

### Before Asking

1. Check this guide again
2. Search existing GitHub issues
3. Read error messages carefully
4. Check service status pages (Railway, Vercel, OpenAI)

### What to Include in Bug Reports

- Error message (full text)
- Steps to reproduce
- Environment (local vs. production)
- Browser/OS version
- Screenshots/logs

---

## Next Steps

**You've deployed successfully! Now:**

1. **Customize content:** Edit chapters in `docs/`
2. **Add features:** Extend API endpoints in `server/`
3. **Improve UI:** Modify React components in `src/components/`
4. **Add analytics:** Integrate Google Analytics or Vercel Analytics
5. **Share your work:** Post on social media, get feedback!

---

## Appendix

### Project Structure

```
physical-AI/
├── docs/                    # 10 textbook chapters (markdown)
├── src/
│   ├── components/          # React components (ChatbotWidget, etc.)
│   ├── pages/              # Custom pages (homepage)
│   ├── css/                # Styling
│   └── theme/              # Docusaurus theme customization
├── server/                  # Main backend (use this one)
│   ├── auth/               # User authentication
│   ├── personalize/        # Content personalization
│   ├── translate/          # Urdu translation
│   ├── rag/                # RAG chatbot
│   ├── agents/             # AI agents
│   ├── tests/              # Test suite
│   ├── main.py             # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── rag/                     # Legacy RAG backend (deprecated)
├── .github/workflows/       # CI/CD pipelines
├── package.json            # Frontend dependencies
├── docusaurus.config.js    # Docusaurus configuration
├── vercel.json             # Vercel deployment config
├── railway.json            # Railway deployment config
└── README.md               # Project overview
```

### Environment Variables Reference

**Complete list of all environment variables:**

```env
# Database
DATABASE_URL                  # PostgreSQL connection string
JWT_SECRET                    # Random string for JWT signing
JWT_ALGORITHM                 # HS256 (default)
ACCESS_TOKEN_EXPIRE_DAYS      # 7 (default)

# AI Providers
OPENAI_API_KEY               # OpenAI API key
CLAUDE_API_KEY               # Anthropic Claude key (optional)
GEMINI_API_KEY               # Google Gemini key (optional)

# Vector Database
QDRANT_URL                   # Qdrant cluster URL
QDRANT_API_KEY               # Qdrant API key

# Feature Flags
DEMO_MODE                    # true/false
FEATURE_TRANSLATION          # true/false
FEATURE_PERSONALIZATION      # true/false
FEATURE_RAG_CHAT            # true/false

# CORS & Networking
ALLOWED_ORIGINS              # Comma-separated URLs
PORT                         # 8000 (default)

# Development
NODE_ENV                     # development/production
LOG_LEVEL                    # INFO (default)
DEBUG                        # true/false
```

---

## Conclusion

Congratulations! You've successfully deployed a production-ready AI-powered textbook with:

- ✅ Interactive chatbot
- ✅ Personalization
- ✅ Translation
- ✅ Scalable architecture
- ✅ Secure configuration

**Share your deployment URL and show it off!**

For questions, open an issue on GitHub or consult the documentation.

**Happy teaching and learning!** 🚀📚🤖

---

*Last Updated: 2025-12-17*
*Version: 3.0 - Complete Rewrite for Beginners*
