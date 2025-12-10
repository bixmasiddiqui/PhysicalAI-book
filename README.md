# Physical AI & Humanoid Robotics Textbook

🤖 An AI-native interactive textbook with RAG chatbot, personalization, and multilingual support.

## 🌟 Features

### Core Textbook
- ✅ **10 Comprehensive Chapters** covering Physical AI and Humanoid Robotics
- 📚 Complete with learning objectives, theory, code examples, and quizzes
- 🎯 Progressive difficulty from fundamentals to advanced topics

### AI-Powered Features
- 🤖 **RAG Chatbot** - Ask questions about any chapter with AI-powered answers
- ✨ **Personalization** - Content adapts to your skill level and background
- 🌐 **Urdu Translation** - Full multilingual support
- 💬 **Selected Text Queries** - Highlight text and ask specific questions
- 📝 **Chapter-Specific Chat** - Focus AI responses on current chapter

### Technical Stack
- **Frontend**: Docusaurus v3, React
- **Backend**: FastAPI, Python
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Serverless Postgres
- **AI**: OpenAI GPT-4, Embeddings
- **Deployment**: GitHub Pages

## 📋 Table of Contents

1. **Fundamentals of Physical AI Systems**
2. **Mathematical Foundations for Robotics**
3. **Programming for Robotics with ROS**
4. **Sensors and Perception Systems**
5. **Actuators and Control Systems**
6. **Machine Learning for Robotics**
7. **Motion Planning and Navigation**
8. **Computer Vision for Robotics**
9. **Humanoid Robot Systems**
10. **Future of Physical AI and Ethics**

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key
- Qdrant Cloud account
- Neon Postgres database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/physical-AI.git
   cd physical-AI
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd rag
   pip install -r requirements.txt
   cd ..
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

5. **Initialize database**
   ```bash
   cd rag/api
   python database.py
   ```

6. **Embed documents**
   ```bash
   python embed_docs.py
   ```

### Running Locally

1. **Start the backend**
   ```bash
   cd rag
   uvicorn api.main:app --reload
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   npm start
   ```

3. **Visit** `http://localhost:3000`

## 🏗️ Project Structure

```
physical-AI/
├── docs/                      # Markdown chapters
│   ├── intro.md
│   ├── chapter-01.md
│   └── ...
├── src/                       # React components
│   ├── components/
│   │   ├── ChatbotWidget.jsx
│   │   └── ChapterActions.jsx
│   ├── pages/
│   └── css/
├── rag/                       # RAG backend
│   ├── api/
│   │   ├── main.py           # FastAPI app
│   │   ├── rag_engine.py     # Vector search
│   │   ├── openai_agent.py   # AI responses
│   │   └── database.py       # Postgres models
│   ├── loaders/
│   │   └── document_loader.py
│   └── utils/
│       └── text_splitter.py
├── personalization/           # Personalization engine
│   └── personalization_engine.py
├── agents/                    # Claude subagents
│   ├── book_writer_agent.py
│   ├── translation_agent.py
│   └── ...
├── auth/                      # Better Auth setup
├── i18n/                      # Translations
│   └── ur/                    # Urdu translations
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Pages deployment
├── docusaurus.config.js
├── sidebars.js
├── package.json
└── README.md
```

## 🎯 Features Walkthrough

### 1. RAG Chatbot

The chatbot uses Retrieval-Augmented Generation to answer questions:

```javascript
// Ask a question about any chapter
POST /ask
{
  "message": "Explain forward kinematics",
  "chapter": "chapter-02",
  "user_id": "user123"
}
```

**How it works:**
1. Embeds your question using OpenAI
2. Searches Qdrant for relevant content
3. Generates answer with GPT-4 using retrieved context
4. Stores conversation in Neon Postgres

### 2. Personalization System

Content adapts to your background:

```python
# Set your profile
POST /update-profile
{
  "user_id": "user123",
  "education_level": "undergraduate",
  "programming_background": "intermediate",
  "math_background": "strong",
  "hardware_background": "beginner"
}

# Get personalized chapter
POST /personalize
{
  "chapter": "chapter-01",
  "user_id": "user123"
}
```

**Difficulty Levels:**
- **Beginner**: Simple language, lots of examples
- **Intermediate**: Balanced theory and practice
- **Expert**: Advanced concepts, mathematical rigor

### 3. Urdu Translation

Translate any chapter to Urdu:

```python
from agents.translation_agent import TranslationAgent

translator = TranslationAgent(openai_api_key=API_KEY)

# Translate single chapter
translator.translate_chapter_file(
    'docs/chapter-01.md',
    'i18n/ur/docusaurus-plugin-content-docs/current/chapter-01.md'
)

# Batch translate all chapters
translator.batch_translate_docs('docs', 'i18n/ur/docusaurus-plugin-content-docs/current')
```

### 4. Selected Text Queries

Highlight any text and ask questions about it:

```javascript
POST /ask-selected-text
{
  "selected_text": "The Zero Moment Point (ZMP) is...",
  "question": "Explain this in simple terms",
  "user_id": "user123"
}
```

## 🤖 Claude Subagents

Reusable agents for content creation:

### Book Writer Agent
```python
from agents.book_writer_agent import BookWriterAgent

writer = BookWriterAgent(api_key=OPENAI_API_KEY)
chapter = writer.write_chapter(
    topic="Soft Robotics Fundamentals",
    chapter_number=11
)
```

### Translation Agent
```python
from agents.translation_agent import TranslationAgent

translator = TranslationAgent(api_key=OPENAI_API_KEY)
urdu_content = translator.translate_to_urdu(chapter_content)
```

### RAG Builder Agent
Handles document embedding and vector search setup.

### Personalization Agent
Rewrites content based on user profiles.

## 📊 API Endpoints

### RAG Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/embed` | POST | Embed all documents into Qdrant |
| `/query` | POST | Search for relevant documents |
| `/ask` | POST | Ask a question with AI response |
| `/ask-selected-text` | POST | Query about selected text |
| `/chat-history/{user_id}` | GET | Retrieve chat history |

### Personalization & Translation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/personalize` | POST | Get personalized chapter |
| `/translate` | POST | Translate chapter to Urdu |
| `/update-profile` | POST | Update user profile |
| `/profile/{user_id}` | GET | Get user profile |

## 🔧 Configuration

### Qdrant Cloud Setup

1. Create a cluster at [qdrant.io/cloud](https://qdrant.io/cloud)
2. Get your API key and cluster URL
3. Add to `.env`:
   ```
   QDRANT_URL=https://xyz-example.qdrant.io
   QDRANT_API_KEY=your_key_here
   ```

### Neon Postgres Setup

1. Create database at [neon.tech](https://neon.tech)
2. Get connection string
3. Add to `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
   ```

### OpenAI Setup

1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

## 🚀 Deployment

### GitHub Pages

1. Update `docusaurus.config.js`:
   ```javascript
   url: 'https://your-username.github.io',
   baseUrl: '/physical-AI/',
   organizationName: 'your-username',
   projectName: 'physical-AI',
   ```

2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. Enable GitHub Pages in repository settings

### Backend Deployment

Deploy FastAPI backend to:
- **Render**: Easy Python deployment
- **Railway**: Simple with Postgres
- **Fly.io**: Global edge deployment
- **AWS Lambda**: Serverless option

## 📝 Environment Variables

```bash
# Required
OPENAI_API_KEY=          # OpenAI API key
QDRANT_URL=              # Qdrant cluster URL
QDRANT_API_KEY=          # Qdrant API key
DATABASE_URL=            # Neon Postgres connection string

# Optional
REACT_APP_API_URL=       # Backend URL for frontend
AUTH_SECRET=             # Better Auth secret
NODE_ENV=                # development/production
```

## 🎓 Educational Use

This textbook is designed for:
- **University Students**: Undergraduate/graduate robotics courses
- **Self-Learners**: Anyone interested in Physical AI
- **Researchers**: Quick reference for robotics concepts
- **Developers**: Practical code examples and implementations

## 🤝 Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Adding New Chapters

```python
from agents.book_writer_agent import BookWriterAgent

writer = BookWriterAgent(api_key=OPENAI_API_KEY)
new_chapter = writer.write_chapter(
    topic="Your Topic Here",
    chapter_number=11
)

# Save to docs/chapter-11.md
with open('docs/chapter-11.md', 'w') as f:
    f.write(new_chapter)
```

## 📄 License

MIT License - feel free to use for educational purposes!

## 🙏 Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/)
- Powered by [OpenAI](https://openai.com/)
- Vector search by [Qdrant](https://qdrant.io/)
- Database by [Neon](https://neon.tech/)

## 📧 Contact

For questions or feedback:
- GitHub Issues: [Create an issue](https://github.com/your-username/physical-AI/issues)
- Email: your-email@example.com

---

**Built with ❤️ for the future of Physical AI education**
#   P h y s i c a l A I - b o o k  
 