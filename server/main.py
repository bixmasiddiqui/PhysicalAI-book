"""
FastAPI main application for Physical AI Textbook Backend
Provides: Auth, Personalization, Translation, RAG, and Agent endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from agents.routes import router as agents_router
from auth.routes import router as auth_router
from personalize.routes import router as personalize_router
from translate.routes import router as translate_router  # STEP E
from rag.routes import router as rag_router  # STEP F

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("Starting Physical AI Textbook API Server...")
    print(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    yield
    print("Shutting down server...")

# Initialize FastAPI app
app = FastAPI(
    title="Physical AI Textbook API",
    description="Backend for personalized, multilingual robotics textbook with RAG chatbot",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://*.vercel.app",
        "https://*.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and deployment verification"""
    return {
        "status": "ok",
        "service": "Physical AI Textbook API",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/auth/*",
            "agents": "/api/agent/*",
            "personalize": "/api/personalize",
            "translate": "/api/translate"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Physical AI Textbook API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Mount routers
app.include_router(agents_router, prefix="/api/agent", tags=["Agents"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(personalize_router, prefix="/api", tags=["Personalization"])
app.include_router(translate_router, prefix="/api", tags=["Translation"])  # STEP E
app.include_router(rag_router, prefix="/api/rag", tags=["RAG Chatbot"])  # STEP F

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
