"""
Tests for Authentication Module
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.database import Base, get_db
from main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuthSignup:
    """Test user signup functionality"""

    def test_signup_success(self):
        """Test successful user registration"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "onboarding": {
                    "role": "Student",
                    "programming_experience": "Beginner",
                    "robotics_experience": "None",
                    "preferred_language": "English",
                    "hardware_availability": "None"
                }
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

    def test_signup_duplicate_email(self):
        """Test signup with existing email fails"""
        # Create first user
        client.post(
            "/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "Pass123!",
                "onboarding": {"role": "Student"}
            }
        )

        # Try to create duplicate
        response = client.post(
            "/auth/signup",
            json={
                "email": "duplicate@example.com",
                "password": "Pass456!",
                "onboarding": {"role": "Student"}
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_invalid_email(self):
        """Test signup with invalid email format"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "not-an-email",
                "password": "Pass123!",
                "onboarding": {"role": "Student"}
            }
        )

        assert response.status_code == 422  # Validation error

    def test_signup_weak_password(self):
        """Test signup with weak password"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "test@example.com",
                "password": "123",
                "onboarding": {"role": "Student"}
            }
        )

        assert response.status_code == 400


class TestAuthLogin:
    """Test user login functionality"""

    def test_login_success(self):
        """Test successful login"""
        # Create user
        client.post(
            "/auth/signup",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!",
                "onboarding": {"role": "Student"}
            }
        )

        # Login
        response = client.post(
            "/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """Test login with incorrect password"""
        # Create user
        client.post(
            "/auth/signup",
            json={
                "email": "user@example.com",
                "password": "CorrectPass123!",
                "onboarding": {"role": "Student"}
            }
        )

        # Try wrong password
        response = client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "WrongPass123!"
            }
        )

        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Pass123!"
            }
        )

        assert response.status_code == 401


class TestAuthProfile:
    """Test user profile endpoints"""

    def test_get_profile_authenticated(self):
        """Test getting profile with valid token"""
        # Signup
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "profile@example.com",
                "password": "Pass123!",
                "onboarding": {
                    "role": "Researcher",
                    "programming_experience": "Advanced"
                }
            }
        )
        token = signup_response.json()["access_token"]

        # Get profile
        response = client.get(
            "/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "profile@example.com"
        assert data["onboarding"]["role"] == "Researcher"

    def test_get_profile_unauthenticated(self):
        """Test getting profile without token fails"""
        response = client.get("/auth/profile")

        assert response.status_code == 401

    def test_get_profile_invalid_token(self):
        """Test getting profile with invalid token"""
        response = client.get(
            "/auth/profile",
            headers={"Authorization": "Bearer invalid-token-here"}
        )

        assert response.status_code == 401


class TestAuthHealth:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test auth health endpoint"""
        response = client.get("/auth/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["module"] == "authentication"
