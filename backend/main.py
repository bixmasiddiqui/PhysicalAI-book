"""
Physical AI Backend - Main Entry Point
Unified backend server for auth, RAG, personalization, and translation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers from server module
from server.agents.routes import router as agents_router
from server.auth.routes import router as auth_router
from server.personalize.routes import router as personalize_router
from server.translate.routes import router as translate_router
from server.rag.routes import router as rag_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("Starting Physical AI Textbook API Server...")
    print(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"CORS Origins: {os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000')}")
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
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
            "translate": "/api/translate",
            "rag": "/api/rag/*"
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
app.include_router(translate_router, prefix="/api", tags=["Translation"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG Chatbot"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
