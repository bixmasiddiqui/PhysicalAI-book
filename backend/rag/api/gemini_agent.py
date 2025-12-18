"""
Gemini Agent - Simple chatbot using Google's Gemini API
No RAG needed - works directly with chapter content
"""

import os
import google.generativeai as genai
from typing import Dict, Optional

class GeminiAgent:
    def __init__(self, api_key: str):
        """Initialize Gemini Agent"""
        genai.configure(api_key=api_key)
        # Try multiple model names in case some are not available
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            try:
                self.model = genai.GenerativeModel('gemini-pro')
            except:
                self.model = genai.GenerativeModel('models/gemini-pro')

        self.system_prompt = """You are an expert AI teaching assistant for the Physical AI & Humanoid Robotics textbook.

Your role is to:
1. Answer questions clearly and accurately about robotics and AI
2. Provide detailed explanations with examples when needed
3. Help students understand complex concepts
4. Suggest related topics for deeper learning

Guidelines:
- Use clear, educational language appropriate for students
- Include relevant examples when helpful
- Encourage hands-on practice and experimentation
"""

    async def ask(self, question: str, chapter: Optional[str] = None, user_id: str = "anonymous") -> Dict:
        """
        Ask a question and get AI-generated answer
        """
        try:
            # Build the prompt
            if chapter:
                prompt = f"""{self.system_prompt}

Question about {chapter}: {question}

Please provide a comprehensive answer about Physical AI and Robotics."""
            else:
                prompt = f"""{self.system_prompt}

Question: {question}

Please provide a comprehensive answer about Physical AI and Robotics."""

            # Get response from Gemini
            response = self.model.generate_content(prompt)

            return {
                'answer': response.text,
                'sources': [{'title': 'Gemini AI', 'type': 'ai_generated'}],
                'question': question
            }

        except Exception as e:
            return {
                'answer': f"I encountered an error: {str(e)}. Please try again.",
                'sources': [],
                'question': question
            }

    async def ask_selected(self, selected_text: str, question: str, user_id: str = "anonymous") -> Dict:
        """
        Ask a question about specifically selected text
        """
        try:
            prompt = f"""{self.system_prompt}

The student has selected this text from the textbook:
"{selected_text}"

Question about this text: {question}

Please answer based on the selected text."""

            response = self.model.generate_content(prompt)

            return {
                'answer': response.text,
                'sources': [{'type': 'selected_text', 'content': selected_text[:500]}],
                'question': question
            }

        except Exception as e:
            return {
                'answer': f"I encountered an error: {str(e)}. Please try again.",
                'sources': [],
                'question': question
            }
