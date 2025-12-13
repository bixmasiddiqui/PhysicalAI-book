"""
Database models for authentication and user profiles
Uses Neon Serverless Postgres
"""

from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Boolean, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/physical_ai")

# Handle Neon's connection pooling
if "neon.tech" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model with onboarding data"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Onboarding data (stored as JSON)
    onboarding = Column(JSON, default={})
    # Structure:
    # {
    #   "role": "Student|Professional|Researcher|Instructor",
    #   "programming_experience": "Beginner|Intermediate|Advanced",
    #   "robotics_experience": "None|Simulation-only|Hardware",
    #   "preferred_language": "English|Urdu|Other",
    #   "hardware_availability": "RTX Workstation|Cloud|Jetson Kit|None"
    # }

class ChatHistory(Base):
    """RAG chatbot conversation history"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    message = Column(String, nullable=False)
    response = Column(String, nullable=False)
    chapter_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PersonalizationCache(Base):
    """Cache for personalized chapter content"""
    __tablename__ = "personalization_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    chapter_id = Column(String(50), index=True, nullable=False)
    profile_hash = Column(String(64), index=True, nullable=False)
    personalized_content = Column(Text, nullable=False)
    applied_transformations = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)

class PersonalizationLog(Base):
    """Log personalization requests for analytics"""
    __tablename__ = "personalization_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    chapter_id = Column(String(50), nullable=False)
    transformation_type = Column(String(100))
    response_time_ms = Column(Integer)
    cached = Column(Boolean, default=False)
    llm_provider = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

class TranslationCache(Base):
    """Cache for translated chapter content"""
    __tablename__ = "translation_cache"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(String(50), index=True, nullable=False)
    language = Column(String(10), index=True, nullable=False)  # 'urdu' for Urdu
    content_hash = Column(String(64), index=True, nullable=False)  # MD5 hash for cache invalidation
    translated_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Initializing database: {DATABASE_URL[:50]}...")
    init_db()
