"""
Tests for Translation Module
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Create a test user and return auth token"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "translate_test@example.com",
            "password": "TestPass123!",
            "onboarding": {
                "role": "Student",
                "programming_experience": "Intermediate",
                "preferred_language": "Urdu"
            }
        }
    )
    return response.json()["access_token"]


class TestTranslateEndpoint:
    """Test translation API endpoint"""

    def test_translate_unauthenticated(self):
        """Test translation without authentication fails"""
        response = client.post(
            "/api/translate",
            json={
                "chapter_id": "chapter-01",
                "target_language": "urdu"
            }
        )

        assert response.status_code == 401

    def test_translate_missing_chapter_id(self, auth_token):
        """Test translation without chapter_id"""
        response = client.post(
            "/api/translate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"target_language": "urdu"}
        )

        assert response.status_code == 422  # Validation error

    def test_translate_invalid_language(self, auth_token):
        """Test translation with unsupported language"""
        response = client.post(
            "/api/translate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chapter_id": "chapter-01",
                "target_language": "french"  # Not supported
            }
        )

        # Should either validate or handle gracefully
        assert response.status_code in [400, 422, 500]

    def test_translate_invalid_chapter(self, auth_token):
        """Test translation with non-existent chapter"""
        response = client.post(
            "/api/translate",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "chapter_id": "chapter-999",
                "target_language": "urdu"
            }
        )

        assert response.status_code == 404


class TestTranslateCacheStats:
    """Test translation cache statistics"""

    def test_cache_stats_authenticated(self, auth_token):
        """Test getting translation cache stats"""
        response = client.get(
            "/api/translate/cache-stats",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_cached" in data
        assert "languages" in data
        assert "hit_rate" in data

    def test_cache_stats_unauthenticated(self):
        """Test cache stats without authentication"""
        response = client.get("/api/translate/cache-stats")

        assert response.status_code == 401


class TestTranslateHealth:
    """Test translation health endpoint"""

    def test_health_check(self):
        """Test translation health endpoint"""
        response = client.get("/api/translate/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["module"] == "translation"
        assert "glossary_terms" in data
        assert data["glossary_terms"] > 0  # Should have glossary loaded


class TestGlossary:
    """Test glossary functionality"""

    def test_glossary_loaded(self):
        """Test that glossary is properly loaded"""
        from translate.translator import UrduTranslator

        translator = UrduTranslator()
        assert len(translator.glossary_terms) > 100

        # Check for specific terms
        assert "ROS" in translator.glossary_terms
        assert "Python" in translator.glossary_terms
        assert "URDF" in translator.glossary_terms
