"""
Demo Mode - Mock LLM Responses
Use this when you don't have API keys for testing
"""

import time
from typing import Dict, Any


class DemoPersonalizer:
    """Mock personalization without API calls"""

    def personalize(self, content: str, user_profile: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Return demo personalized content"""

        # Simulate processing time
        time.sleep(1)

        role = user_profile.get("role", "Student")
        experience = user_profile.get("programming_experience", "Beginner")

        # Add personalization header
        personalized = f"""
> **Personalized for {role} - {experience} Level** 🎯

{content}

---

### 💡 Personalization Applied

Based on your profile ({role}, {experience} level), this content has been:
- Simplified for your experience level
- Enhanced with relevant examples for your role
- Structured for optimal learning

*Note: This is DEMO MODE. In production, content is fully rewritten by Claude AI to match your exact needs.*
"""

        metadata = {
            "processing_time_ms": 1000,
            "profile_hash": "demo123",
            "llm_provider": "demo",
            "fallback_used": True,
            "demo_mode": True
        }

        return personalized, metadata


class DemoTranslator:
    """Mock translation without API calls"""

    def __init__(self):
        # Simple word-by-word translation for demo
        self.glossary = {
            "robot": "روبوٹ",
            "robotics": "روبوٹکس",
            "sensor": "سینسر",
            "motor": "موٹر",
            "ROS": "ROS",  # Technical terms stay English
            "Python": "Python",
            "programming": "پروگرامنگ",
            "code": "کوڈ",
            "computer": "کمپیوٹر",
            "software": "سافٹ ویئر",
            "hardware": "ہارڈ ویئر",
            "chapter": "باب",
            "introduction": "تعارف",
            "system": "نظام",
        }

    def translate(self, content: str, target_language: str = "urdu") -> tuple[str, Dict[str, Any]]:
        """Return demo translated content"""

        # Simulate processing time
        time.sleep(1.5)

        # For demo, we'll just add Urdu headers and some translated text
        translated = f"""
# تعارف - Introduction

> **یہ ڈیمو موڈ میں ترجمہ ہے**
> **This is a DEMO translation**

{content}

---

### 📝 ترجمہ کی تفصیلات (Translation Details)

اصل پیداوار میں، یہ مکمل طور پر اردو میں Claude AI کے ذریعے ترجمہ کیا جائے گا۔

*In production, this would be fully translated to Urdu by Claude AI with:*
- 200+ technical term glossary
- Context-aware translation
- RTL (right-to-left) rendering
- Code blocks preserved in English
- Technical accuracy maintained

**Demo Mode Active** - Get free API keys to see real translation!
"""

        metadata = {
            "processing_time_ms": 1500,
            "content_hash": "demo123",
            "llm_provider": "demo",
            "fallback_used": True,
            "demo_mode": True
        }

        return translated, metadata


class DemoRAG:
    """Mock RAG chatbot without API calls"""

    def __init__(self):
        self.responses = {
            "ros": "ROS (Robot Operating System) is a flexible framework for writing robot software. It provides tools, libraries, and conventions to simplify the task of creating complex robot behavior across robotics platforms.\n\n*Demo Mode: Get API keys for real AI-powered answers with citations!*",
            "python": "Python is a high-level programming language widely used in robotics. It's beginner-friendly and has excellent libraries for robot control, machine learning, and data processing.\n\n*Demo Mode Active*",
            "sensor": "Sensors are devices that detect changes in the environment and send information to the robot's computer. Common types include cameras, LiDAR, ultrasonic sensors, and IMUs.\n\n*Demo Mode Active*",
            "default": "I'm running in DEMO MODE without API keys. I can only give pre-written answers. To get real AI-powered responses:\n\n1. Get free Claude API key from console.anthropic.com ($5 free)\n2. Add it to server/.env file\n3. Restart the backend\n\nThen I can answer ANY question about robotics with citations from the textbook!"
        }

    def query(self, message: str, chapter_id: str = None) -> Dict[str, Any]:
        """Return demo chat response"""

        # Simulate processing time
        time.sleep(0.5)

        # Simple keyword matching
        message_lower = message.lower()
        response = self.responses["default"]

        for keyword, answer in self.responses.items():
            if keyword in message_lower:
                response = answer
                break

        return {
            "answer": response,
            "sources": [
                {
                    "chapter_id": chapter_id or "chapter-01",
                    "section": "Demo Section",
                    "relevance_score": 0.85,
                    "demo_mode": True
                }
            ],
            "conversation_id": None,
            "metadata": {
                "query_time_ms": 500,
                "demo_mode": True,
                "model_used": "demo"
            }
        }


# Singleton instances
demo_personalizer = DemoPersonalizer()
demo_translator = DemoTranslator()
demo_rag = DemoRAG()
