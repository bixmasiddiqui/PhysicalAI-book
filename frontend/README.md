# Physical AI Textbook - Frontend

Interactive Docusaurus-based textbook interface with AI chatbot, personalization, and translation features.

## Features

- 📚 **10 Comprehensive Chapters** - Physical AI and Humanoid Robotics content
- 💬 **AI Chatbot** - Floating widget for Q&A on any page
- ✨ **Personalization** - Adaptive content difficulty
- 🌐 **Translation** - Urdu translation support
- 🎨 **Modern UI** - Clean, responsive design

## Tech Stack

- **Framework:** Docusaurus v3.1
- **UI Library:** React 18.2
- **Styling:** CSS Modules
- **HTTP Client:** Axios
- **Deployment:** Vercel

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
# Edit .env.local and set your backend URL
```

Example `.env.local`:
```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm start
```

Frontend runs at: `http://localhost:3000`

## Project Structure

```
frontend/
├── docs/                  # Markdown textbook chapters
│   ├── intro.md          # Introduction
│   ├── chapter-01.md     # Chapter 1-10
│   └── ...
│
├── src/
│   ├── components/       # React components
│   │   ├── ChatbotWidget.jsx        # Floating chatbot
│   │   ├── PersonalizeButton.jsx    # Personalization
│   │   ├── TranslateButton.jsx      # Translation
│   │   ├── DocPageActions.jsx       # Combined actions
│   │   └── AuthMenu.jsx             # Authentication UI
│   │
│   ├── pages/           # Custom pages
│   │   └── index.js    # Homepage
│   │
│   ├── css/            # Global styles
│   │   └── custom.css
│   │
│   └── theme/          # Docusaurus theme overrides
│       └── Root.js     # App wrapper (includes ChatbotWidget)
│
├── static/             # Static assets (images, etc.)
│
├── docusaurus.config.js   # Docusaurus configuration
├── sidebars.js           # Sidebar structure
├── package.json          # Dependencies
└── vercel.json          # Vercel deployment config
```

## Available Scripts

### Development

```bash
npm start          # Start dev server
npm run build      # Build for production
npm run serve      # Serve production build locally
npm run clear      # Clear cache
```

### Documentation

```bash
npm run write-translations  # Generate translation files
npm run write-heading-ids   # Add heading IDs
```

### Deployment

```bash
npm run deploy     # Deploy to GitHub Pages
```

## Components

### ChatbotWidget

Floating chatbot button that appears on all pages.

**Location:** `src/theme/Root.js`

**Features:**
- Connects to backend `/api/rag/ask` endpoint
- Supports chapter-specific queries
- Displays sources and citations
- Fallback to mock responses if backend unavailable

### DocPageActions

Combines Personalize and Translate buttons for chapter pages.

**Usage in MDX:**
```mdx
import DocPageActions from '@site/src/components/DocPageActions';

<DocPageActions chapter="chapter-01" />
```

### PersonalizeButton

Fetches personalized version of chapter content.

**API:** `POST /api/personalize`

### TranslateButton

Translates chapter to Urdu with technical glossary.

**API:** `POST /api/translate`

## Environment Variables

### Development (`.env.local`)

```env
REACT_APP_API_URL=http://localhost:8000
```

### Production (Vercel Dashboard)

Set environment variable:
- **Name:** `REACT_APP_API_URL`
- **Value:** `https://your-backend.railway.app`
- **Scope:** Production, Preview, Development

## Deployment

### Deploy to Vercel

#### Option 1: Vercel CLI

```bash
npm install -g vercel
vercel login
vercel
```

#### Option 2: GitHub Integration

1. Push code to GitHub
2. Import project in Vercel dashboard
3. Configure:
   - **Framework Preset:** Docusaurus
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
4. Add environment variable: `REACT_APP_API_URL`
5. Deploy

#### Option 3: Vercel Button

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Deploy to GitHub Pages

1. Update `docusaurus.config.js`:
   ```js
   url: 'https://your-username.github.io',
   baseUrl: '/physical-AI/',
   organizationName: 'your-username',
   projectName: 'physical-AI',
   ```

2. Deploy:
   ```bash
   GIT_USER=your-username npm run deploy
   ```

## Customization

### Update Content

Edit markdown files in `docs/` directory:

```bash
docs/
├── intro.md              # Introduction
├── chapter-01.md         # Fundamentals
├── chapter-02.md         # Math Foundations
└── ...
```

### Modify Theme

Edit `src/css/custom.css` for global styles:

```css
:root {
  --ifm-color-primary: #2e8555;
  --ifm-font-family-base: 'Inter', sans-serif;
}
```

### Add Custom Pages

Create new files in `src/pages/`:

```jsx
// src/pages/about.js
export default function About() {
  return <div>About Page</div>;
}
```

Access at: `http://localhost:3000/about`

## Configuration

### docusaurus.config.js

Main configuration file. Key settings:

```js
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Master the Future of AI-Powered Robotics',
  url: 'https://your-domain.com',
  baseUrl: '/',

  // Navbar, footer, theme settings...
}
```

### sidebars.js

Controls sidebar structure:

```js
module.exports = {
  tutorialSidebar: [
    'intro',
    'chapter-01',
    'chapter-02',
    // ...
  ],
};
```

## Troubleshooting

### Issue: Chatbot not appearing

**Check:**
1. `src/theme/Root.js` includes `<ChatbotWidget />`
2. Backend is running
3. CORS configured correctly
4. Browser console for errors

**Solution:**
```bash
# Hard refresh
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

### Issue: Connection Error in chatbot

**Check:**
1. Backend URL in `.env.local` or Vercel env vars
2. Backend `/health` endpoint responds
3. CORS allows your frontend domain

**Solution:**
```bash
# Test backend
curl https://your-backend.railway.app/health
```

### Issue: Build fails

**Check:**
1. Node version (>=18.0)
2. Dependencies installed
3. No TypeScript errors

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Best Practices

### 1. Component Organization

- Keep components small and focused
- Use CSS Modules for styling
- Extract reusable logic to hooks

### 2. Performance

- Use `React.memo()` for expensive components
- Lazy load images with `loading="lazy"`
- Minimize API calls with caching

### 3. Accessibility

- Use semantic HTML
- Add ARIA labels where needed
- Test with keyboard navigation

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Build production bundle
5. Submit PR

## License

MIT License - see LICENSE file

## Support

- Docusaurus Docs: https://docusaurus.io
- Issues: GitHub Issues
- Deployment Help: See DEPLOYMENT_GUIDE.md

---

**Happy building!** 🚀
