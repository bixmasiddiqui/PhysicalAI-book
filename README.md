# Physical AI & Humanoid Robotics Textbook

An AI-native interactive textbook with RAG chatbot, personalization, and multilingual support.

## 🎯 Project Structure

This project is separated into independent frontend and backend:

```
physical-AI/
├── frontend/          # Docusaurus textbook interface
│   ├── docs/         # Markdown chapters
│   ├── src/          # React components
│   └── README.md     # Frontend documentation
│
├── backend/           # FastAPI server
│   ├── server/       # Main app code
│   ├── rag/          # RAG engine
│   └── README.md     # Backend documentation
│
└── README.md         # This file
```

## 🚀 Quick Start

### Frontend (Docusaurus)

```bash
cd frontend
npm install
npm start
```

Runs at: http://localhost:3000

[**Full Frontend Documentation →**](./frontend/README.md)

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at: http://localhost:8000

[**Full Backend Documentation →**](./backend/README.md)

## 📚 Features

### Frontend
- 📖 **10 Comprehensive Chapters** - Physical AI content
- 💬 **Floating AI Chatbot** - Available on every page
- ✨ **Personalization Buttons** - Adapt content to user level
- 🌐 **Translation Buttons** - Urdu translation
- 🎨 **Modern UI** - Clean, responsive design

### Backend
- 🔐 **Authentication** - JWT-based user auth
- 🤖 **RAG Chatbot** - Document search + AI responses
- ✨ **Personalization** - Content adaptation engine
- 🌐 **Translation** - Urdu translation with glossary
- 🎯 **AI Agents** - Code explainer, quiz generator

## 🛠️ Tech Stack

### Frontend
- **Framework:** Docusaurus v3.1
- **UI:** React 18.2
- **HTTP:** Axios
- **Deploy:** Vercel

### Backend
- **Framework:** FastAPI 0.109
- **Database:** PostgreSQL / SQLite
- **Vector DB:** Qdrant Cloud
- **AI:** OpenAI, Gemini, Claude
- **Deploy:** Railway / Render

## 📖 Documentation

- [Frontend README](./frontend/README.md) - Complete frontend guide
- [Backend README](./backend/README.md) - Complete backend guide
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production deployment
- [Fixes Applied](./FIXES_APPLIED.md) - Recent changes

## 🌐 Deployment

### Frontend → Vercel

```bash
cd frontend
vercel
```

See [frontend/README.md](./frontend/README.md#deployment) for details.

### Backend → Railway

```bash
cd backend
railway init
railway up
```

See [backend/README.md](./backend/README.md#deployment) for details.

## 🔧 Environment Variables

### Frontend (.env.local)

```env
REACT_APP_API_URL=http://localhost:8000
```

### Backend (.env)

```env
DATABASE_URL=sqlite:///./physical_ai.db
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
JWT_SECRET=your-secret
ALLOWED_ORIGINS=http://localhost:3000
```

See `.env.example` files in each directory for complete templates.

## 📊 Development Workflow

### 1. Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm start
```

### 3. Access

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🧪 Testing

### Frontend

```bash
cd frontend
npm test
```

### Backend

```bash
cd backend
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes in appropriate directory (frontend/ or backend/)
4. Test locally
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## 📁 Repository Structure

See [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) for detailed file organization.

## 🐛 Troubleshooting

### Frontend Issues

**Chatbot not appearing:**
- Check backend is running
- Verify `REACT_APP_API_URL` is set
- Check browser console for errors

**Build fails:**
- Clear cache: `npm run clear`
- Reinstall: `rm -rf node_modules && npm install`

### Backend Issues

**Import errors:**
- Ensure running from `backend/` directory
- Check `PYTHONPATH` if needed

**CORS errors:**
- Update `ALLOWED_ORIGINS` in backend `.env`
- Include your frontend URL

See individual README files for more troubleshooting.

## 📜 License

MIT License - see [LICENSE](./LICENSE) file

## 🙏 Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- AI by OpenAI, Google Gemini, Anthropic Claude

## 📞 Support

- **Frontend Issues:** See [frontend/README.md](./frontend/README.md)
- **Backend Issues:** See [backend/README.md](./backend/README.md)
- **Deployment:** See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/physical-AI/issues)

---

**Built with ❤️ for robotics education**

🚀 **Get Started:** Choose [Frontend](./frontend/) or [Backend](./backend/) and check their README files!
