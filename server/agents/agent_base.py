"""
Base Agent Class for Claude Code Subagents
Handles spec validation, AI invocation, and response formatting
"""

import yaml
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import os

class AgentBase:
    """Base class for all Claude Code agents"""

    def __init__(self, agent_name: str, api_key: Optional[str] = None):
        self.agent_name = agent_name
        self.spec = self._load_spec()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('CLAUDE_API_KEY')

        if not self.api_key:
            raise ValueError("API key required: set OPENAI_API_KEY or CLAUDE_API_KEY")

    def _load_spec(self) -> Dict[str, Any]:
        """Load agent specification from YAML file"""
        spec_path = Path(__file__).parent.parent.parent / "spec" / "agents" / f"{self.agent_name}.yaml"

        if not spec_path.exists():
            raise FileNotFoundError(f"Agent spec not found: {spec_path}")

        with open(spec_path, 'r') as f:
            return yaml.safe_load(f)

    def validate_input(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inputs against spec"""
        spec_inputs = self.spec.get('inputs', {})
        validated = {}

        for field_name, field_spec in spec_inputs.items():
            value = inputs.get(field_name)

            # Check required fields
            if field_spec.get('required', False) and value is None:
                raise ValueError(f"Required field missing: {field_name}")

            # Use default if not provided
            if value is None and 'default' in field_spec:
                value = field_spec['default']

            # Type validation (basic)
            if value is not None:
                expected_type = field_spec.get('type')
                if expected_type == 'string' and not isinstance(value, str):
                    raise ValueError(f"{field_name} must be string")
                elif expected_type == 'integer' and not isinstance(value, int):
                    raise ValueError(f"{field_name} must be integer")
                elif expected_type == 'array' and not isinstance(value, list):
                    raise ValueError(f"{field_name} must be array")

                # Enum validation
                if 'enum' in field_spec and value not in field_spec['enum']:
                    raise ValueError(f"{field_name} must be one of {field_spec['enum']}")

                # Length validation for strings
                if expected_type == 'string' and 'max_length' in field_spec:
                    if len(value) > field_spec['max_length']:
                        raise ValueError(f"{field_name} exceeds max length {field_spec['max_length']}")

                # Range validation for integers
                if expected_type == 'integer':
                    if 'min' in field_spec and value < field_spec['min']:
                        raise ValueError(f"{field_name} below minimum {field_spec['min']}")
                    if 'max' in field_spec and value > field_spec['max']:
                        raise ValueError(f"{field_name} above maximum {field_spec['max']}")

            validated[field_name] = value

        return validated

    def render_prompt(self, inputs: Dict[str, Any]) -> str:
        """Render prompt template with inputs using Jinja2-like syntax"""
        template = self.spec.get('prompt_template', '')

        # Simple template rendering (for production, use Jinja2)
        rendered = template
        for key, value in inputs.items():
            if value is not None:
                # Handle arrays
                if isinstance(value, list):
                    rendered = rendered.replace(f"{{{{question_types | join(', ')}}}}", ", ".join(value))
                    rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
                else:
                    rendered = rendered.replace(f"{{{{{key}}}}}", str(value))

        # Remove conditional blocks if variable not set (basic implementation)
        import re
        # Remove {% if var %}...{% endif %} blocks where var is not in inputs
        for match in re.finditer(r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}', rendered, re.DOTALL):
            var_name = match.group(1)
            if var_name not in inputs or inputs[var_name] is None:
                rendered = rendered.replace(match.group(0), '')
            else:
                # Keep content, remove tags
                rendered = rendered.replace(match.group(0), match.group(2))

        return rendered.strip()

    async def invoke_ai(self, prompt: str) -> str:
        """Invoke AI API (OpenAI or Claude) - to be implemented by subclasses or use default"""
        # Check which API to use
        if os.getenv('OPENAI_API_KEY'):
            return await self._invoke_openai(prompt)
        elif os.getenv('CLAUDE_API_KEY'):
            return await self._invoke_claude(prompt)
        else:
            raise ValueError("No AI API key configured")

    async def _invoke_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert AI assistant for a Physical AI and Humanoid Robotics textbook."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _invoke_claude(self, prompt: str) -> str:
        """Call Claude API"""
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)

            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent"""
        start_time = time.time()

        # Validate inputs
        validated_inputs = self.validate_input(inputs)

        # Render prompt
        prompt = self.render_prompt(validated_inputs)

        # Invoke AI
        ai_response = await self.invoke_ai(prompt)

        # Parse response (basic - override in subclasses for structured output)
        result = self.parse_response(ai_response, validated_inputs)

        # Add metadata
        result['metadata'] = result.get('metadata', {})
        result['metadata']['processing_time'] = round(time.time() - start_time, 2)
        result['metadata']['agent'] = self.agent_name
        result['metadata']['timestamp'] = datetime.utcnow().isoformat()

        return result

    def parse_response(self, ai_response: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured output - override in subclasses"""
        return {"response": ai_response}
