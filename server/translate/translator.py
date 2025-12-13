"""
Urdu Translator using LLM
Handles translation with technical term preservation
"""

import os
import json
from pathlib import Path
from typing import Tuple, List
import anthropic
from openai import OpenAI

class UrduTranslator:
    """LLM-based translator for technical content"""

    def __init__(self):
        """Initialize translator with LLM provider"""
        self.llm_provider = os.getenv("LLM_PROVIDER", "claude")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Load glossary
        glossary_path = Path(__file__).parent / "glossary.json"
        with open(glossary_path, 'r', encoding='utf-8') as f:
            self.glossary_data = json.load(f)

        # Flatten all terms
        self.glossary_terms = self._flatten_glossary()

    def _flatten_glossary(self) -> List[str]:
        """Flatten glossary categories into single list"""
        terms = []
        for category, term_list in self.glossary_data["categories"].items():
            terms.extend(term_list)
        return list(set(terms))  # Remove duplicates

    def build_translation_prompt(self, content: str) -> str:
        """
        Build LLM prompt for translation

        Args:
            content: English markdown content to translate

        Returns:
            Complete prompt with instructions and content
        """
        # Build glossary string (first 100 terms for brevity)
        glossary_sample = ", ".join(self.glossary_terms[:100])
        if len(self.glossary_terms) > 100:
            glossary_sample += f", ... and {len(self.glossary_terms) - 100} more"

        prompt = f"""You are an expert technical translator specializing in robotics and AI content.

Translate the following English textbook chapter to Urdu. Follow these CRITICAL RULES:

1. PRESERVATION RULES (NEVER TRANSLATE THESE):
   - Technical terms: {glossary_sample}
   - Code blocks (```...```)
   - LaTeX equations ($...$ and $$...$$)
   - Function names, variable names, class names
   - File paths, URLs, links
   - Acronyms (ROS, API, SDK, CNN, etc.)
   - Programming language names (Python, C++, JavaScript)
   - Software/tool names (Docker, Git, Gazebo, etc.)

2. FORMATTING RULES:
   - Preserve all markdown structure (headers #, lists -, tables |)
   - Keep code blocks exactly as they are
   - Maintain spacing and indentation
   - Preserve links [text](url) - translate text, keep URL
   - Keep images ![alt](url) - translate alt text, keep URL

3. TRANSLATION QUALITY:
   - Use natural, fluent Urdu (not word-by-word literal translation)
   - Use technical Urdu where appropriate (e.g., "روبوٹکس" for robotics field)
   - But keep specific technical terms in English (e.g., "ROS" not translated)
   - Maintain academic/educational tone
   - Right-to-left (RTL) compatible output

4. SPECIAL CASES:
   - Code comments: Keep in English
   - Mathematical symbols: Keep as-is
   - Unit measurements: Keep in English (e.g., "5 meters", "10 Hz")

IMPORTANT: Return ONLY the translated markdown. Do not add explanations, notes, or metadata.

---

CONTENT TO TRANSLATE:

{content}

---

TRANSLATED URDU MARKDOWN:
"""
        return prompt

    async def translate(self, content: str, target_language: str = "urdu") -> Tuple[str, int]:
        """
        Translate content to target language

        Args:
            content: Source English content
            target_language: Target language (default: urdu)

        Returns:
            Tuple of (translated_content, tokens_used)
        """
        if target_language != "urdu":
            raise ValueError(f"Unsupported target language: {target_language}")

        # Build prompt
        prompt = self.build_translation_prompt(content)

        # Try primary provider (Claude)
        if self.llm_provider == "claude" and self.claude_api_key:
            try:
                return await self._call_claude(prompt)
            except Exception as e:
                print(f"Claude translation failed: {str(e)}")
                # Fall back to OpenAI
                if self.openai_api_key:
                    print("Falling back to OpenAI...")
                    return await self._call_openai(prompt)
                else:
                    raise

        # Use OpenAI
        elif self.openai_api_key:
            return await self._call_openai(prompt)

        else:
            raise ValueError("No LLM API key configured. Set CLAUDE_API_KEY or OPENAI_API_KEY")

    async def _call_claude(self, prompt: str) -> Tuple[str, int]:
        """
        Call Claude API for translation

        Args:
            prompt: Complete translation prompt

        Returns:
            Tuple of (translated_content, tokens_used)
        """
        try:
            client = anthropic.Anthropic(api_key=self.claude_api_key)

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=16000,  # Long enough for full chapter
                temperature=0.3,  # Lower for consistency
                system="You are an expert technical translator for robotics and AI textbooks.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            translated_content = response.content[0].text.strip()

            # Estimate tokens (input + output)
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return translated_content, tokens_used

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def _call_openai(self, prompt: str) -> Tuple[str, int]:
        """
        Call OpenAI API for translation

        Args:
            prompt: Complete translation prompt

        Returns:
            Tuple of (translated_content, tokens_used)
        """
        try:
            client = OpenAI(api_key=self.openai_api_key)

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical translator for robotics and AI textbooks."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            translated_content = response.choices[0].message.content.strip()

            # Get token usage
            tokens_used = response.usage.total_tokens

            return translated_content, tokens_used

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def validate_translation(self, original: str, translated: str) -> bool:
        """
        Validate translation quality (basic checks)

        Args:
            original: Original English content
            translated: Translated Urdu content

        Returns:
            True if validation passes, False otherwise
        """
        # Check 1: Translated content is not empty
        if not translated or len(translated.strip()) < 10:
            return False

        # Check 2: Code blocks preserved (count should match)
        original_code_blocks = original.count("```")
        translated_code_blocks = translated.count("```")
        if original_code_blocks != translated_code_blocks:
            return False

        # Check 3: LaTeX equations preserved
        original_latex = original.count("$")
        translated_latex = translated.count("$")
        if original_latex != translated_latex:
            return False

        # Check 4: Links preserved
        original_links = original.count("](")
        translated_links = translated.count("](")
        if original_links != translated_links:
            return False

        # Validation passed
        return True
