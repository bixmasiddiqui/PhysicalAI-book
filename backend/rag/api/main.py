"""
FastAPI RAG Backend for Physical AI Textbook
Provides endpoints for document embedding, querying, and chat
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Try to import RAG engine and OpenAI agent (optional)
try:
    from .rag_engine import RAGEngine
    from .openai_agent import OpenAIRAGAgent
    RAG_AVAILABLE = True
except Exception as e:
    print(f"RAG not available: {e}")
    RAG_AVAILABLE = False

# Import Gemini agent (simple alternative)
try:
    from .gemini_agent import GeminiAgent
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Gemini not available: {e}")
    GEMINI_AVAILABLE = False

# Try to import database, but make it optional
try:
    from .database import get_db, ChatHistory, UserProfile, PersonalizationCache
    DATABASE_AVAILABLE = True
except Exception as e:
    print(f"Database not available: {e}")
    DATABASE_AVAILABLE = False
    # Create a dummy get_db for when database is not available
    def get_db():
        return None

# Try to import personalization engine
try:
    from personalization.personalization_engine import PersonalizationEngine
    PERSONALIZATION_AVAILABLE = True
except Exception as e:
    print(f"Personalization not available: {e}")
    PERSONALIZATION_AVAILABLE = False

load_dotenv()

app = FastAPI(title="Physical AI Textbook RAG API")

# CORS middleware - Configure allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Set ALLOWED_ORIGINS in .env for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Agent (try Gemini first, fallback to OpenAI)
ai_agent = None
rag_engine = None

if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    print("Using Gemini AI Agent")
    ai_agent = GeminiAgent(api_key=os.getenv("GEMINI_API_KEY"))
elif RAG_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    print("Using OpenAI RAG Agent")
    rag_engine = RAGEngine(
        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    ai_agent = OpenAIRAGAgent(
        api_key=os.getenv("OPENAI_API_KEY"),
        rag_engine=rag_engine
    )
else:
    print("WARNING: No AI agent available. Please set GEMINI_API_KEY or OPENAI_API_KEY")

# Initialize Personalization Engine (if available)
if PERSONALIZATION_AVAILABLE and os.getenv("OPENAI_API_KEY"):
    personalization_engine = PersonalizationEngine(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    personalization_engine = None

# Request/Response Models
class EmbedRequest(BaseModel):
    docs_path: str = "./docs"

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anonymous"
    chapter: Optional[str] = None

class SelectedTextRequest(BaseModel):
    selected_text: str
    question: str
    user_id: Optional[str] = "anonymous"

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    conversation_id: Optional[int] = None

class PersonalizeRequest(BaseModel):
    chapter: str
    user_id: str
    difficulty: Optional[str] = None

class UserProfileUpdate(BaseModel):
    user_id: str
    education_level: str
    programming_background: str
    math_background: str
    hardware_background: str

class TranslateRequest(BaseModel):
    chapter: str
    target_language: str = "ur"

@app.get("/")
async def root():
    return {
        "message": "Physical AI Textbook RAG API",
        "version": "1.0.0",
        "endpoints": [
            "/embed",
            "/query",
            "/search",
            "/ask",
            "/ask-selected-text",
            "/personalize",
            "/translate",
            "/update-profile",
            "/profile/{user_id}",
            "/chat-history/{user_id}",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/embed")
async def embed_documents(request: EmbedRequest):
    """
    Embed all documents from the docs folder into Qdrant vector database
    """
    try:
        result = await rag_engine.embed_all_documents(request.docs_path)
        return {
            "status": "success",
            "message": f"Embedded {result['num_documents']} documents",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(request: QueryRequest):
    """
    Query the vector database for relevant documents
    """
    try:
        results = await rag_engine.query(request.question, top_k=request.top_k)
        return {
            "question": request.question,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(request: QueryRequest):
    """
    Simple semantic search without AI response generation
    """
    try:
        results = await rag_engine.search(request.question, top_k=request.top_k)
        return {
            "query": request.question,
            "documents": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, db=Depends(get_db) if DATABASE_AVAILABLE else None):
    """
    Ask a question about the textbook with AI-generated response
    Uses Gemini or OpenAI to generate answer
    """
    try:
        if not ai_agent:
            raise HTTPException(status_code=503, detail="AI agent not configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in .env file")

        # Get AI response
        response = await ai_agent.ask(
            question=request.message,
            chapter=request.chapter,
            user_id=request.user_id
        )

        # Save to chat history (if database available)
        conversation_id = None
        if DATABASE_AVAILABLE and db:
            chat_entry = ChatHistory(
                user_id=request.user_id,
                message=request.message,
                response=response['answer'],
                sources=str(response['sources'])
            )
            db.add(chat_entry)
            db.commit()
            db.refresh(chat_entry)
            conversation_id = chat_entry.id

        return ChatResponse(
            answer=response['answer'],
            sources=response['sources'],
            conversation_id=conversation_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-selected-text", response_model=ChatResponse)
async def ask_about_selected_text(request: SelectedTextRequest, db=Depends(get_db) if DATABASE_AVAILABLE else None):
    """
    Ask a question about specifically selected text
    Uses AI to answer based on the selected text
    """
    try:
        if not ai_agent:
            raise HTTPException(status_code=503, detail="AI agent not configured. Please set GEMINI_API_KEY or OPENAI_API_KEY in .env file")

        # Use the selected text as context
        response = await ai_agent.ask_selected(
            selected_text=request.selected_text,
            question=request.question,
            user_id=request.user_id
        )

        # Save to chat history (if database available)
        conversation_id = None
        if DATABASE_AVAILABLE and db:
            chat_entry = ChatHistory(
                user_id=request.user_id,
                message=f"[Selected Text Query] {request.question}",
                response=response['answer'],
                sources=request.selected_text[:200]
            )
            db.add(chat_entry)
            db.commit()
            conversation_id = chat_entry.id

        return ChatResponse(
            answer=response['answer'],
            sources=[{"content": request.selected_text, "type": "selected"}],
            conversation_id=conversation_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20, db=Depends(get_db)):
    """
    Retrieve chat history for a user
    """
    try:
        history = db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.created_at.desc()).limit(limit).all()

        return {
            "user_id": user_id,
            "history": [
                {
                    "id": entry.id,
                    "message": entry.message,
                    "response": entry.response,
                    "timestamp": entry.created_at.isoformat()
                }
                for entry in history
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/personalize")
async def personalize_chapter(request: PersonalizeRequest, db=Depends(get_db)):
    """
    Personalize a chapter for a specific user based on their profile
    """
    try:
        # Get user profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == request.user_id
        ).first()

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found. Please complete onboarding first."
            )

        # Check cache
        cached = db.query(PersonalizationCache).filter(
            PersonalizationCache.user_id == request.user_id,
            PersonalizationCache.chapter == request.chapter,
            PersonalizationCache.difficulty_level == (request.difficulty or 'auto')
        ).first()

        if cached:
            return {
                "personalized_content": cached.personalized_content,
                "difficulty": cached.difficulty_level,
                "cached": True
            }

        # Load chapter content
        chapter_path = f"./docs/{request.chapter}.md"
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
        except:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Personalize
        user_profile_dict = {
            'education_level': user_profile.education_level,
            'programming_background': user_profile.programming_background,
            'math_background': user_profile.math_background,
            'hardware_background': user_profile.hardware_background
        }

        personalized = personalization_engine.personalize_chapter(
            chapter_content=chapter_content,
            user_profile=user_profile_dict,
            difficulty=request.difficulty
        )

        # Cache the result
        cache_entry = PersonalizationCache(
            user_id=request.user_id,
            chapter=request.chapter,
            difficulty_level=request.difficulty or 'auto',
            personalized_content=personalized
        )
        db.add(cache_entry)
        db.commit()

        return {
            "personalized_content": personalized,
            "difficulty": request.difficulty or 'auto',
            "cached": False
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_chapter(request: TranslateRequest):
    """
    Translate a chapter to the target language (Urdu)
    Uses Gemini AI for translation
    """
    try:
        # Load chapter content
        chapter_path = f"./docs/{request.chapter}.md"
        try:
            with open(chapter_path, 'r', encoding='utf-8') as f:
                chapter_content = f.read()
        except:
            raise HTTPException(status_code=404, detail="Chapter not found")

        # Use Gemini to translate
        if not GEMINI_AVAILABLE or not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(status_code=503, detail="Translation requires Gemini API key")

        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""You are an expert translator specializing in technical and educational content.
Translate the following robotics textbook chapter from English to Urdu.

IMPORTANT Instructions:
- Keep markdown formatting (headings, lists, code blocks)
- Keep technical terms in English with Urdu explanations in parentheses
- Keep code examples unchanged
- Keep mathematical formulas unchanged

Chapter content:
{chapter_content}

Translate to Urdu:"""

        response = model.generate_content(prompt)
        translated_content = response.text

        return {
            "translated_content": translated_content,
            "target_language": request.target_language,
            "chapter": request.chapter
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-profile")
async def update_user_profile(profile: UserProfileUpdate, db=Depends(get_db)):
    """
    Update or create user profile for personalization
    """
    try:
        existing = db.query(UserProfile).filter(
            UserProfile.user_id == profile.user_id
        ).first()

        if existing:
            existing.education_level = profile.education_level
            existing.programming_background = profile.programming_background
            existing.math_background = profile.math_background
            existing.hardware_background = profile.hardware_background
        else:
            new_profile = UserProfile(
                user_id=profile.user_id,
                education_level=profile.education_level,
                programming_background=profile.programming_background,
                math_background=profile.math_background,
                hardware_background=profile.hardware_background
            )
            db.add(new_profile)

        db.commit()

        return {"status": "success", "message": "Profile updated"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str, db=Depends(get_db)):
    """
    Get user profile for personalization
    """
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "user_id": profile.user_id,
        "education_level": profile.education_level,
        "programming_background": profile.programming_background,
        "math_background": profile.math_background,
        "hardware_background": profile.hardware_background
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
