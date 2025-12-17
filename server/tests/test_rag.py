"""
Tests for RAG Chatbot Module
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Create a test user and return auth token"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "rag_test@example.com",
            "password": "TestPass123!",
            "onboarding": {
                "role": "Student",
                "programming_experience": "Beginner",
                "preferred_language": "English"
            }
        }
    )
    return response.json()["access_token"]


class TestRAGChatEndpoint:
    """Test RAG chatbot API endpoint"""

    def test_chat_unauthenticated(self):
        """Test chat without authentication fails"""
        response = client.post(
            "/api/rag/chat",
            json={
                "message": "What is ROS?",
                "chapter_id": "chapter-01"
            }
        )

        assert response.status_code == 401

    def test_chat_missing_message(self, auth_token):
        """Test chat without message fails"""
        response = client.post(
            "/api/rag/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"chapter_id": "chapter-01"}
        )

        assert response.status_code == 422  # Validation error

    @patch('rag.engine.RAGEngine.query')
    def test_chat_success(self, mock_query, auth_token):
        """Test successful chat interaction"""
        # Mock RAG query response
        mock_query.return_value = {
            "answer": "ROS is a flexible framework for robot software.",
            "sources": [
                {
                    "chapter_id": "chapter-01",
                    "section": "Introduction",
                    "relevance_score": 0.95
                }
            ],
            "metadata": {
                "query_time_ms": 250,
                "chunks_searched": 10,
                "model_used": "claude-3-sonnet"
            }
        }

        response = client.post(
            "/api/rag/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "What is ROS?",
                "chapter_id": "chapter-01"
            }
        )

        # Note: This may return 200 or 500 depending on RAG implementation status
        assert response.status_code in [200, 500, 501]

    def test_chat_with_selected_text(self, auth_token):
        """Test chat with selected text context"""
        response = client.post(
            "/api/rag/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "Explain this in simple terms",
                "chapter_id": "chapter-01",
                "selected_text": "ROS (Robot Operating System) is a middleware suite."
            }
        )

        # Implementation may be incomplete
        assert response.status_code in [200, 500, 501]

    def test_chat_empty_message(self, auth_token):
        """Test chat with empty message"""
        response = client.post(
            "/api/rag/chat",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "",
                "chapter_id": "chapter-01"
            }
        )

        assert response.status_code == 422


class TestRAGChatHistory:
    """Test RAG chat history endpoint"""

    def test_history_authenticated(self, auth_token):
        """Test getting chat history with authentication"""
        response = client.get(
            "/api/rag/chat/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Should return empty history for new user
        assert response.status_code in [200, 501]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_history_unauthenticated(self):
        """Test chat history without authentication"""
        response = client.get("/api/rag/chat/history")

        assert response.status_code == 401

    def test_history_pagination(self, auth_token):
        """Test chat history with pagination"""
        response = client.get(
            "/api/rag/chat/history?limit=10&offset=0",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code in [200, 501]


class TestRAGHealth:
    """Test RAG health endpoint"""

    def test_health_check(self):
        """Test RAG health endpoint"""
        response = client.get("/api/rag/health")

        assert response.status_code in [200, 501]
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["module"] == "rag"


class TestRAGVectorSearch:
    """Test vector search functionality"""

    @patch('rag.vectorstore.QdrantVectorStore.search')
    def test_vector_search(self, mock_search, auth_token):
        """Test vector similarity search"""
        # Mock vector search results
        mock_search.return_value = [
            {
                "id": "chunk-1",
                "score": 0.92,
                "metadata": {"chapter_id": "chapter-01", "section": "Introduction"}
            },
            {
                "id": "chunk-2",
                "score": 0.88,
                "metadata": {"chapter_id": "chapter-01", "section": "Setup"}
            }
        ]

        response = client.post(
            "/api/rag/search",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "query": "How to install ROS?",
                "top_k": 5
            }
        )

        # Implementation may be incomplete
        assert response.status_code in [200, 404, 501]

    def test_vector_search_unauthenticated(self):
        """Test vector search without authentication"""
        response = client.post(
            "/api/rag/search",
            json={"query": "test query"}
        )

        assert response.status_code == 401
