"""
Content Transformer using LLM (Claude or OpenAI)
Transforms chapter content based on user profile
"""

import os
from typing import Dict, List, Tuple
import asyncio

class ContentTransformer:
    """Transforms content using LLM based on user profile"""

    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "claude")
        self.api_key = os.getenv("CLAUDE_API_KEY") if self.llm_provider == "claude" else os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(f"API key not configured for {self.llm_provider}")

    def determine_transformations(self, onboarding: dict) -> List[str]:
        """Determine which transformations to apply based on user profile"""
        transformations = []

        prog_exp = onboarding.get("programming_experience", "Intermediate")
        robotics_exp = onboarding.get("robotics_experience", "None")
        hardware = onboarding.get("hardware_availability", "None")

        # Programming experience transformations
        if prog_exp == "Beginner":
            transformations.append("beginner-simplify")
            transformations.append("add-code-comments")
        elif prog_exp == "Advanced":
            transformations.append("advanced-depth")
            transformations.append("add-optimizations")

        # Robotics experience transformations
        if robotics_exp == "None":
            transformations.append("add-context")
            transformations.append("add-visual-aids")
        elif robotics_exp == "Hardware":
            transformations.append("practical-tips")
            transformations.append("debugging-guides")

        # Hardware availability transformations
        if hardware == "Jetson Kit":
            transformations.append("jetson-specific")
        elif hardware == "Cloud":
            transformations.append("cloud-deployment")
        elif hardware == "None":
            transformations.append("simulator-alternatives")

        return transformations

    def build_prompt(self, chapter_content: str, transformations: List[str], onboarding: dict) -> str:
        """Build LLM prompt for content transformation"""
        prog_exp = onboarding.get("programming_experience", "Intermediate")
        robotics_exp = onboarding.get("robotics_experience", "None")
        hardware = onboarding.get("hardware_availability", "None")

        prompt = f"""You are an expert educational content adapter for a Physical AI and Robotics textbook.

**User Profile:**
- Programming Experience: {prog_exp}
- Robotics Experience: {robotics_exp}
- Hardware Availability: {hardware}

**Task:** Transform the following textbook chapter to match this learner's needs.

**Transformations to Apply:** {', '.join(transformations)}

**Guidelines:**
"""

        if "beginner-simplify" in transformations:
            prompt += "\n- Simplify technical language and mathematical notation"
            prompt += "\n- Add step-by-step explanations for complex concepts"
            prompt += "\n- Include analogies and real-world examples"

        if "advanced-depth" in transformations:
            prompt += "\n- Add algorithmic complexity analysis"
            prompt += "\n- Include optimization techniques and best practices"
            prompt += "\n- Provide production deployment considerations"

        if "add-code-comments" in transformations:
            prompt += "\n- Add detailed inline comments to all code examples"
            prompt += "\n- Explain what each line does"

        if "simulator-alternatives" in transformations:
            prompt += "\n- For hardware examples, provide simulator alternatives (Gazebo, Webots)"
            prompt += "\n- Include links to free simulation tools"

        if "jetson-specific" in transformations:
            prompt += "\n- Add Jetson Nano/Xavier deployment instructions"
            prompt += "\n- Include CUDA optimization examples"
            prompt += "\n- Add power management considerations"

        if "cloud-deployment" in transformations:
            prompt += "\n- Add AWS/Azure deployment guides"
            prompt += "\n- Include cost estimates for cloud resources"
            prompt += "\n- Provide scaling considerations"

        prompt += """

**Important:**
- Preserve ALL code blocks exactly as-is (only add comments if specified)
- Keep all URLs, links, and image references intact
- Maintain markdown formatting
- DO NOT translate technical terms (ROS, URDF, ZMP, etc.)
- Keep the chapter structure (headings, sections)

**Original Chapter:**

{chapter_content}

**Return ONLY the transformed chapter content in markdown format. Do not add any preamble or explanation.**
"""

        return prompt.replace("{chapter_content}", chapter_content)

    async def transform_content(self, chapter_content: str, onboarding: dict) -> Tuple[str, List[str]]:
        """Transform chapter content using LLM"""
        transformations = self.determine_transformations(onboarding)

        prompt = self.build_prompt(chapter_content, transformations, onboarding)

        try:
            if self.llm_provider == "claude":
                transformed_content = await self._call_claude(prompt)
            else:
                transformed_content = await self._call_openai(prompt)

            return transformed_content, transformations

        except Exception as e:
            print(f"LLM transformation error: {str(e)}")
            # Fallback: return original content
            raise

    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=self.api_key)

        message = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert educational content adapter for robotics textbooks."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )

        return response.choices[0].message.content
