"""Code Explainer Agent Implementation"""

from .agent_base import AgentBase
import json
import re
from typing import Dict, Any, List

class CodeExplainerAgent(AgentBase):
    """Agent for explaining code snippets"""

    def __init__(self, api_key: str = None):
        super().__init__("code-explainer", api_key)

    def parse_response(self, ai_response: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response to extract structured code explanation"""

        sections = {
            'overview': '',
            'line_by_line': [],
            'key_concepts': [],
            'common_pitfalls': [],
            'suggested_modifications': []
        }

        # Split response into sections
        current_section = 'overview'
        current_text = []

        lines = ai_response.split('\n')

        for line in lines:
            line_lower = line.lower().strip()

            # Detect section headers
            if 'overview' in line_lower and line.startswith(('#', '**', '##')):
                if current_text:
                    sections[current_section] = '\n'.join(current_text).strip()
                current_section = 'overview'
                current_text = []

            elif 'line' in line_lower and 'by' in line_lower and line.startswith(('#', '**', '##')):
                if current_text:
                    sections['overview'] = '\n'.join(current_text).strip()
                current_section = 'line_by_line'
                current_text = []

            elif 'key concept' in line_lower and line.startswith(('#', '**', '##')):
                if current_text:
                    sections['line_by_line'] = self._parse_line_by_line('\n'.join(current_text))
                current_section = 'key_concepts'
                current_text = []

            elif 'pitfall' in line_lower and line.startswith(('#', '**', '##')):
                if current_text:
                    sections['key_concepts'] = self._parse_key_concepts('\n'.join(current_text))
                current_section = 'common_pitfalls'
                current_text = []

            elif 'modification' in line_lower or 'variation' in line_lower and line.startswith(('#', '**', '##')):
                if current_text:
                    sections['common_pitfalls'] = self._parse_list('\n'.join(current_text))
                current_section = 'suggested_modifications'
                current_text = []

            else:
                if line.strip():
                    current_text.append(line)

        # Process last section
        if current_text:
            if current_section == 'line_by_line':
                sections['line_by_line'] = self._parse_line_by_line('\n'.join(current_text))
            elif current_section == 'key_concepts':
                sections['key_concepts'] = self._parse_key_concepts('\n'.join(current_text))
            elif current_section == 'common_pitfalls':
                sections['common_pitfalls'] = self._parse_list('\n'.join(current_text))
            elif current_section == 'suggested_modifications':
                sections['suggested_modifications'] = self._parse_modifications('\n'.join(current_text))
            else:
                sections[current_section] = '\n'.join(current_text).strip()

        return sections

    def _parse_line_by_line(self, text: str) -> List[Dict[str, Any]]:
        """Parse line-by-line explanations"""
        results = []
        lines = text.split('\n')

        for line in lines:
            # Look for patterns like "Line 5:" or "5." or "` code ` - explanation"
            match = re.match(r'(?:Line\s+)?(\d+)[:\.\)]\s*`?([^`\-]+)`?\s*[-:]?\s*(.*)', line, re.IGNORECASE)
            if match:
                results.append({
                    "line_number": int(match.group(1)),
                    "code": match.group(2).strip(),
                    "explanation": match.group(3).strip()
                })

        return results

    def _parse_key_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Parse key concepts section"""
        concepts = []
        lines = text.split('\n')

        current_concept = None
        for line in lines:
            # Look for concept headers (bold, numbered, or bullet points)
            if line.strip().startswith(('-', '*', '•')) or re.match(r'^\d+\.', line) or line.strip().startswith('**'):
                if current_concept:
                    concepts.append(current_concept)

                concept_name = re.sub(r'^[-*•]\s*', '', line.strip())
                concept_name = re.sub(r'^\d+\.\s*', '', concept_name)
                concept_name = concept_name.replace('**', '').strip()

                # Extract concept name before colon if present
                if ':' in concept_name:
                    parts = concept_name.split(':', 1)
                    current_concept = {
                        "concept": parts[0].strip(),
                        "explanation": parts[1].strip(),
                        "relevant_lines": []
                    }
                else:
                    current_concept = {
                        "concept": concept_name,
                        "explanation": "",
                        "relevant_lines": []
                    }

            elif current_concept and line.strip():
                # Add to explanation
                current_concept['explanation'] += ' ' + line.strip()

        if current_concept:
            concepts.append(current_concept)

        return concepts

    def _parse_list(self, text: str) -> List[str]:
        """Parse a simple list (pitfalls, etc.)"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith(('-', '*', '•')) or re.match(r'^\d+\.', line):
                item = re.sub(r'^[-*•]\s*', '', line)
                item = re.sub(r'^\d+\.\s*', '', item)
                if item:
                    items.append(item)

        return items

    def _parse_modifications(self, text: str) -> List[Dict[str, str]]:
        """Parse suggested modifications"""
        mods = []
        lines = text.split('\n')

        current_mod = None
        in_code = False
        code_lines = []

        for line in lines:
            if line.strip().startswith('```'):
                in_code = not in_code
                if not in_code and code_lines and current_mod:
                    current_mod['example_code'] = '\n'.join(code_lines)
                    code_lines = []
                continue

            if in_code:
                code_lines.append(line)
            elif line.strip().startswith(('-', '*', '•', '1.', '2.')):
                if current_mod:
                    mods.append(current_mod)

                desc = re.sub(r'^[-*•]\s*', '', line.strip())
                desc = re.sub(r'^\d+\.\s*', '', desc)

                current_mod = {
                    "description": desc,
                    "example_code": ""
                }

        if current_mod:
            mods.append(current_mod)

        return mods
