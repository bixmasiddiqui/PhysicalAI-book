"""
Personalization Engine - Rewrites chapters based on user background
Adapts difficulty level and examples for individual learners
"""

from openai import OpenAI
from typing import Dict, Optional

class PersonalizationEngine:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"

    def personalize_chapter(self, chapter_content: str, user_profile: Dict, difficulty: str = None) -> str:
        """
        Personalize chapter content based on user background
        """
        # Determine difficulty level
        if difficulty is None:
            difficulty = self._determine_difficulty(user_profile)

        # Build personalization prompt
        prompt = self._build_personalization_prompt(chapter_content, user_profile, difficulty)

        # Generate personalized version
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert educational content adapter. Rewrite technical content to match the learner's background and skill level."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        personalized_content = response.choices[0].message.content

        return personalized_content

    def _determine_difficulty(self, user_profile: Dict) -> str:
        """
        Determine appropriate difficulty level from user profile
        """
        education = user_profile.get('education_level', '').lower()
        programming = user_profile.get('programming_background', '').lower()
        math = user_profile.get('math_background', '').lower()

        # Simple scoring system
        score = 0

        # Education level
        if 'phd' in education or 'graduate' in education:
            score += 3
        elif 'bachelor' in education or 'undergraduate' in education:
            score += 2
        elif 'high school' in education:
            score += 1

        # Programming
        if 'expert' in programming or 'advanced' in programming:
            score += 2
        elif 'intermediate' in programming:
            score += 1

        # Math
        if 'advanced' in math or 'strong' in math:
            score += 2
        elif 'intermediate' in math:
            score += 1

        # Determine level
        if score >= 6:
            return 'expert'
        elif score >= 3:
            return 'intermediate'
        else:
            return 'beginner'

    def _build_personalization_prompt(self, content: str, user_profile: Dict, difficulty: str) -> str:
        """
        Build the personalization prompt
        """
        education = user_profile.get('education_level', 'undergraduate')
        programming = user_profile.get('programming_background', 'beginner')
        math = user_profile.get('math_background', 'basic')
        hardware = user_profile.get('hardware_background', 'none')

        difficulty_instructions = {
            'beginner': """
            - Use simple, everyday language
            - Explain all technical terms
            - Use lots of analogies and real-world examples
            - Break down complex concepts into small steps
            - Minimize mathematical notation
            - Provide step-by-step code walkthroughs
            """,
            'intermediate': """
            - Use technical language but explain advanced concepts
            - Provide detailed examples
            - Include some mathematical formulas with explanations
            - Balance theory and practical examples
            - Assume familiarity with basic programming
            """,
            'expert': """
            - Use precise technical language
            - Include rigorous mathematical formulations
            - Focus on advanced concepts and trade-offs
            - Provide concise, optimized code examples
            - Reference research papers and advanced topics
            """
        }

        prompt = f"""Rewrite the following robotics textbook chapter to match this learner profile:

**Learner Background:**
- Education: {education}
- Programming: {programming}
- Mathematics: {math}
- Hardware Experience: {hardware}
- Target Difficulty: {difficulty}

**Instructions for {difficulty.upper()} level:**
{difficulty_instructions[difficulty]}

**Original Chapter Content:**
{content}

**Task:**
Rewrite this chapter to perfectly match the learner's background. Adjust:
1. Language complexity
2. Amount of explanation for concepts
3. Types of examples (relate to their background)
4. Mathematical rigor
5. Code complexity

Maintain the same structure (headings, sections) but adapt the content.
"""

        return prompt

    def generate_personalized_examples(self, concept: str, user_profile: Dict) -> str:
        """
        Generate examples tailored to user's background
        """
        background = user_profile.get('education_level', '')

        prompt = f"""Generate 2-3 examples to illustrate this robotics concept: {concept}

Learner's background: {background}

Make the examples relatable to someone with this background. If they're a student, use academic examples. If they mention a specific field, relate examples to that field.

Concept: {concept}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=800
        )

        return response.choices[0].message.content
