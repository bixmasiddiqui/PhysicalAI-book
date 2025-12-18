"""
Shared Test Fixtures and Configuration
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.database import Base, get_db
from main import app

# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database dependency override
def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply dependency override
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the application"""
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create and drop database tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Standard test user data"""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "onboarding": {
            "role": "Student",
            "programming_experience": "Intermediate",
            "robotics_experience": "None",
            "preferred_language": "English",
            "hardware_availability": "None"
        }
    }


@pytest.fixture
def authenticated_client(test_client, test_user_data):
    """Create authenticated test client with token"""
    # Signup user
    response = test_client.post("/auth/signup", json=test_user_data)
    token = response.json()["access_token"]

    # Add auth header to client
    test_client.headers = {"Authorization": f"Bearer {token}"}
    return test_client


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "content": "# Personalized Content\n\nThis is test content.",
        "metadata": {
            "processing_time_ms": 1500,
            "profile_hash": "test123",
            "llm_provider": "claude",
            "fallback_used": False
        }
    }


@pytest.fixture
def sample_chapter_content():
    """Sample chapter content for testing"""
    return """
# Introduction to ROS

ROS (Robot Operating System) is a flexible framework for writing robot software.

## Key Concepts

- Nodes: Independent processes that perform computation
- Topics: Named buses for message passing
- Services: Request/reply communication

## Getting Started

Install ROS using the following command:
```bash
sudo apt install ros-noetic-desktop-full
```

This chapter will teach you the fundamentals of robotics programming.
"""
