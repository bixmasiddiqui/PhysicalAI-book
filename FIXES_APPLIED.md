# Fixes Applied - Production Deployment Issues

**Date:** 2025-12-17
**Issue:** Deployed site showing old version, chatbot and features not visible

---

## ROOT CAUSES IDENTIFIED

###1. **ChatbotWidget Not Rendered**
- **Location:** `src/theme/Root.js`
- **Problem:** Import and usage were commented out on main branch
- **Impact:** Chatbot never appeared on any page

### 2. **Feature Buttons Not Integrated**
- **Location:** All docs markdown files
- **Problem:** Used hard-coded demo buttons with alerts instead of real React components
- **Impact:** Translation and Personalization features were inaccessible

### 3. **Deployment Branch Mismatch**
- **Problem:** Working on `5-tests-demo-video` branch, but GitHub Actions deploys from `main`
- **Impact:** All changes made on development branch never deployed

### 4. **Backend Not Configured for Production**
- **Problem:** No production API URL set (defaults to localhost:8000)
- **Impact:** Even if chatbot rendered, it would fail to connect to backend

---

## FIXES APPLIED

### ✅ Fix 1: Enabled ChatbotWidget in Root.js

**File:** `src/theme/Root.js`

**Before (main branch):**
```javascript
import React from 'react';
// import ChatbotWidget from '../components/ChatbotWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      {/* <ChatbotWidget /> */}
    </>
  );
}
```

**After:**
```javascript
import React from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

// Wrap the entire app with the chatbot widget
// This makes the chatbot available on every page
export default function Root({children}) {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
}
```

**Result:** Chatbot widget now renders on every page with floating button in bottom-right corner.

---

### ✅ Fix 2: Created DocPageActions Component

**Files Created:**
- `src/components/DocPageActions.jsx`
- `src/components/DocPageActions.module.css`

**Purpose:** Unified component to add Personalize and Translate buttons to documentation pages

**Usage:**
```mdx
---
title: Chapter Title
---

import DocPageActions from '@site/src/components/DocPageActions';

# Chapter Title

<DocPageActions chapter="chapter-01" />

[Rest of content...]
```

**Result:** Real React components (PersonalizeButton, TranslateButton) are now properly integrated

---

### ✅ Fix 3: Updated intro.md as Example

**File:** `docs/intro.md`

**Changed from:**
- Hard-coded HTML buttons with alert() calls
- No actual functionality

**Changed to:**
- Proper MDX import of DocPageActions component
- Functional Personalize and Translate buttons

**Result:** Introduction page now has working feature buttons

---

### ✅ Fix 4: Fixed Missing Dependencies

**File:** `rag/requirements.txt`

**Added:**
- `google-generativeai==0.3.2` (for Gemini AI support)
- `sqlalchemy==2.0.25` (for database operations)

**Result:** Backend dependencies complete

---

### ✅ Fix 5: Fixed CORS Configuration

**File:** `rag/api/main.py`

**Changed from:**
```python
allow_origins=["*"]  # Allows all origins - SECURITY RISK
```

**Changed to:**
```python
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Environment-based configuration
    ...
)
```

**Result:** CORS now configurable via environment variable, more secure

---

## REMAINING TASKS TO DEPLOY

### 🔴 HIGH PRIORITY - Required for Deployment

#### Task 1: Update All Chapter Files

**Action Required:** Add DocPageActions to all 10 chapter files

**Template for each chapter:**
```mdx
---
sidebar_position: N
title: Chapter Title
---

import DocPageActions from '@site/src/components/DocPageActions';

# Chapter N: Title

<DocPageActions chapter="chapter-0N" />

[Rest of chapter content...]
```

**Files to update:**
- `docs/chapter-01.md`
- `docs/chapter-02.md`
- `docs/chapter-03.md`
- `docs/chapter-04.md`
- `docs/chapter-05.md`
- `docs/chapter-06.md`
- `docs/chapter-07.md`
- `docs/chapter-08.md`
- `docs/chapter-09.md`
- `docs/chapter-10.md`

---

#### Task 2: Merge to Main Branch

**Current situation:**
- Working on: `5-tests-demo-video` branch
- Deployment from: `main` branch only (configured in `.github/workflows/deploy.yml`)

**Actions required:**

```bash
# Step 1: Commit all fixes on current branch
git add .
git commit -m "Fix: Enable chatbot, integrate feature buttons, update dependencies"

# Step 2: Switch to main branch
git checkout main

# Step 3: Merge fixes from development branch
git merge 5-tests-demo-video

# Step 4: Push to GitHub (triggers deployment)
git push origin main
```

**Result:** GitHub Actions will automatically build and deploy to GitHub Pages

---

#### Task 3: Deploy Backend to Production

**Current state:** Backend only runs locally (localhost:8000)

**Options:**

**Option A: Railway (Recommended)**
1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select repository
4. Root Directory: `server`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (see section below)
7. Deploy

**Option B: Render**
1. Go to [render.com](https://render.com)
2. New Web Service from GitHub
3. Root Directory: `server`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy

**Required Environment Variables:**
```env
DATABASE_URL=<neon-postgres-connection-string>
OPENAI_API_KEY=<your-openai-key>
QDRANT_URL=<your-qdrant-cluster-url>
QDRANT_API_KEY=<your-qdrant-api-key>
JWT_SECRET=<random-32-char-string>
ALLOWED_ORIGINS=https://your-vercel-domain.github.io,http://localhost:3000
DEMO_MODE=false
PORT=8000
```

**Get your backend URL after deployment** (e.g., `https://physical-ai-production.up.railway.app`)

---

#### Task 4: Configure Frontend to Use Production Backend

**Two approaches:**

**Approach A: Using GitHub Secrets (Recommended for GitHub Pages)**

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add secret: `REACT_APP_API_URL` = `https://your-backend-url.railway.app`
3. Update `.github/workflows/deploy.yml` to include environment variable:

```yaml
- name: Build website
  run: npm run build
  env:
    REACT_APP_API_URL: ${{ secrets.REACT_APP_API_URL }}
```

**Approach B: Using Vercel (Alternative to GitHub Pages)**

1. Deploy to Vercel instead of GitHub Pages
2. Add environment variable in Vercel dashboard:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-backend-url.railway.app`
3. Redeploy

**Result:** Frontend will connect to production backend instead of localhost

---

### 🟡 MEDIUM PRIORITY - Recommended

#### Task 5: Embed Documents to Vector Database

**Purpose:** Allow RAG chatbot to search through textbook content

**Action:**
```bash
# Using Railway CLI
railway login
railway link  # Select your backend project
railway run python -c "from rag.routes import embed_all_documents; import asyncio; asyncio.run(embed_all_documents('../docs'))"
```

**Or via API:**
```bash
curl -X POST https://your-backend.railway.app/api/rag/embed \
  -H "Content-Type: application/json" \
  -d '{"docs_path": "./docs"}'
```

**Cost:** ~$0.50-1.00 (one-time OpenAI embedding cost)
**Time:** 2-5 minutes

---

#### Task 6: Set Up Environment Variables Template

**Create:** `.env.production.example` (already exists in repo)

**Content example:**
```env
# Production Environment Variables Template
# Copy these to your deployment platform (Railway, Render, Vercel)

DATABASE_URL=postgresql://user:pass@your-neon-db.neon.tech/dbname?sslmode=require
OPENAI_API_KEY=sk-your-production-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
JWT_SECRET=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALLOWED_ORIGINS=https://your-deployed-frontend.com
DEMO_MODE=false
```

---

## VERIFICATION CHECKLIST

After completing all tasks, verify:

### Frontend Checklist
- [ ] Visit deployed site (GitHub Pages URL)
- [ ] Homepage loads correctly
- [ ] Navigate to Introduction page
- [ ] See Personalize and Translate buttons (not demo alerts)
- [ ] See floating chatbot button (💬) in bottom-right corner
- [ ] Click chatbot button - modal opens
- [ ] All chapters accessible

### Backend Checklist
- [ ] Visit backend health endpoint: `https://your-backend.railway.app/health`
- [ ] Returns: `{"status": "ok", ...}`
- [ ] Check API docs: `https://your-backend.railway.app/docs`
- [ ] OpenAPI documentation loads

### End-to-End Integration Checklist
- [ ] Open chatbot on deployed site
- [ ] Type a test question (e.g., "What is Physical AI?")
- [ ] Chatbot responds (not "Error" or "Connection failed")
- [ ] Response includes sources from chapters
- [ ] Click Personalize button on a chapter
- [ ] Personalization works (or shows appropriate loading/error)
- [ ] Click Translate button
- [ ] Translation works (or shows appropriate loading/error)

---

## TESTING COMMANDS

### Local Testing (Before Deploying)

**Terminal 1 - Backend:**
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
npm install
npm start
```

**Open:** http://localhost:3000

### Production Testing

**Test Health:**
```bash
curl https://your-backend.railway.app/health
```

**Test Chatbot API:**
```bash
curl -X POST https://your-backend.railway.app/api/rag/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Physical AI?", "user_id": "test"}'
```

---

## TROUBLESHOOTING

### Issue: Chatbot still not appearing

**Check:**
1. Browser cache cleared (Ctrl+Shift+R)
2. Root.js changes merged to main
3. GitHub Actions deployment successful
4. No build errors in GitHub Actions logs

**Solution:**
```bash
# Force rebuild
git commit --allow-empty -m "Force rebuild"
git push origin main
```

---

### Issue: Chatbot shows "Connection Error"

**Check:**
1. Backend is running (`curl https://your-backend.railway.app/health`)
2. `REACT_APP_API_URL` environment variable set
3. CORS configured correctly (includes your frontend domain)

**Solution:**
- Verify backend logs for CORS errors
- Update `ALLOWED_ORIGINS` in backend environment variables

---

### Issue: Features return 404 or 500 errors

**Check:**
1. Backend routes exist (`/api/personalize`, `/api/translate`)
2. Database connection working
3. API keys set correctly

**Solution:**
- Check backend logs for specific error
- Verify all environment variables set
- Test endpoints individually via Postman/curl

---

## DEPLOYMENT TIMELINE

**Estimated time to go live:**

| Task | Time | Status |
|------|------|--------|
| Update chapter files | 30 min | ⏳ Pending |
| Merge to main | 5 min | ⏳ Pending |
| GitHub Pages deploy | 3-5 min | ⏳ Auto |
| Deploy backend | 10 min | ⏳ Pending |
| Configure frontend env | 5 min | ⏳ Pending |
| Test end-to-end | 10 min | ⏳ Pending |
| **TOTAL** | **~60 min** | |

---

## SUMMARY OF CHANGES

✅ **Fixed:** ChatbotWidget now renders on all pages
✅ **Fixed:** Created reusable DocPageActions component
✅ **Fixed:** Updated intro.md with real React components
✅ **Fixed:** Added missing backend dependencies
✅ **Fixed:** Secured CORS configuration
✅ **Created:** Comprehensive deployment guide
✅ **Created:** This fixes documentation

⏳ **Remaining:** Update all 10 chapter files
⏳ **Remaining:** Merge to main and deploy
⏳ **Remaining:** Set up production backend
⏳ **Remaining:** Configure environment variables

---

**Next Steps:** Follow "REMAINING TASKS TO DEPLOY" section above to complete deployment.

---

*Last Updated: 2025-12-17*
*Author: Claude (Senior Full-Stack Engineer)*
