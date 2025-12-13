"""Quiz Generator Agent Implementation"""

from .agent_base import AgentBase
import json
import re
from typing import Dict, Any, List

class QuizGeneratorAgent(AgentBase):
    """Agent for generating educational quizzes"""

    def __init__(self, api_key: str = None):
        super().__init__("quiz-generator", api_key)

    async def invoke_ai(self, prompt: str) -> str:
        """Override to request JSON output"""
        # Append JSON instruction
        prompt += "\n\nReturn ONLY valid JSON array of questions with no additional text."

        return await super().invoke_ai(prompt)

    def parse_response(self, ai_response: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response to extract structured quiz questions"""

        # Try to extract JSON from response
        try:
            # Find JSON array in response
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group(0))
            else:
                # Fallback: try parsing entire response
                questions = json.loads(ai_response)

            if not isinstance(questions, list):
                questions = [questions]

        except json.JSONDecodeError:
            # Fallback: create a simple structure from text
            questions = self._parse_text_questions(ai_response, inputs)

        # Calculate metadata
        difficulty_dist = {}
        for q in questions:
            diff = q.get('difficulty', 'unknown')
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1

        # Estimate time: 1-2 min per question
        estimated_time = len(questions) * 1.5

        return {
            "questions": questions,
            "metadata": {
                "total_questions": len(questions),
                "difficulty_distribution": difficulty_dist,
                "estimated_time_minutes": int(estimated_time)
            }
        }

    def _parse_text_questions(self, text: str, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback parser for non-JSON responses"""
        questions = []
        lines = text.split('\n')

        current_q = None
        for line in lines:
            line = line.strip()

            # Detect question start (numbered)
            if re.match(r'^\d+[\.\)]\s*', line):
                if current_q:
                    questions.append(current_q)

                current_q = {
                    "id": len(questions) + 1,
                    "type": "multiple_choice",
                    "difficulty": inputs.get('difficulty', 'intermediate'),
                    "question": re.sub(r'^\d+[\.\)]\s*', '', line),
                    "options": [],
                    "correct_answer": "",
                    "explanation": "",
                    "topic": "General"
                }

            # Detect options (A, B, C, D or a, b, c, d or -, *)
            elif current_q and re.match(r'^[A-Da-d][\.\)]\s*', line):
                option = re.sub(r'^[A-Da-d][\.\)]\s*', '', line)
                current_q['options'].append(option)

            elif current_q and line.lower().startswith('answer:'):
                current_q['correct_answer'] = line.split(':', 1)[1].strip()

            elif current_q and line.lower().startswith('explanation:'):
                current_q['explanation'] = line.split(':', 1)[1].strip()

        # Add last question
        if current_q:
            questions.append(current_q)

        return questions if questions else [{
            "id": 1,
            "type": "short_answer",
            "difficulty": inputs.get('difficulty', 'intermediate'),
            "question": "Generated from content",
            "correct_answer": "See explanation",
            "explanation": text[:500],
            "topic": "General"
        }]
