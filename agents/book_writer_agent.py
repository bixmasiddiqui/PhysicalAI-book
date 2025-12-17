"""
Book Writer Agent - Generates textbook chapters
Can be reused to create new chapters or expand existing ones
"""

from openai import OpenAI

class BookWriterAgent:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"

    def write_chapter(self, topic: str, chapter_number: int, outline: str = None) -> str:
        """
        Write a complete textbook chapter
        """
        system_prompt = """You are an expert robotics textbook author. Write comprehensive, educational chapters on Physical AI and Humanoid Robotics.

Each chapter must include:
1. **Learning Objectives** - Clear, measurable goals
2. **Theory** - Core concepts explained clearly
3. **Diagrams** - Placeholder ASCII diagrams or descriptions
4. **Practical Tasks** - Hands-on exercises
5. **Code Examples** - Working Python/C++ code
6. **Glossary** - Key terms defined
7. **Checkpoint Quiz** - 3-5 multiple choice questions with answers
8. **AI Assistant Prompts** - Questions for deeper learning

Use markdown formatting with proper structure."""

        user_prompt = f"""Write Chapter {chapter_number}: {topic}

{"Outline: " + outline if outline else ""}

Create a comprehensive chapter following the required structure with:
- Clear explanations suitable for university students
- Practical code examples in Python
- Real-world applications
- Progressive difficulty

Make it educational, engaging, and technically accurate."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        chapter_content = response.choices[0].message.content

        return chapter_content

    def expand_section(self, chapter_content: str, section_name: str) -> str:
        """
        Expand a specific section of a chapter
        """
        prompt = f"""Expand the following section from a robotics textbook chapter:

Section: {section_name}

Current content:
{chapter_content}

Provide a more detailed explanation with:
- Additional examples
- More detailed code
- Practical applications
- Common pitfalls to avoid
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        return response.choices[0].message.content

    def generate_exercises(self, chapter_topic: str, difficulty: str = "intermediate") -> str:
        """
        Generate additional practice exercises
        """
        prompt = f"""Generate 5 practice exercises for this topic: {chapter_topic}

Difficulty level: {difficulty}

Include:
1. Problem statement
2. Required concepts
3. Hints
4. Sample solution approach (no complete code)

Make exercises progressively challenging."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=1500
        )

        return response.choices[0].message.content
