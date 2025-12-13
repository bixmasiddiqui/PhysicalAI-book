"""Summarizer Agent Implementation"""

from .agent_base import AgentBase
import json
import re
from typing import Dict, Any

class SummarizerAgent(AgentBase):
    """Agent for summarizing textbook content"""

    def __init__(self, api_key: str = None):
        super().__init__("summarizer", api_key)

    def parse_response(self, ai_response: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response to extract summary and key points"""

        # Try to find key points (bullet points or numbered list)
        key_points = []
        lines = ai_response.split('\n')

        in_key_points = False
        summary_lines = []

        for line in lines:
            stripped = line.strip()

            # Detect key points section
            if 'key' in stripped.lower() and ('point' in stripped.lower() or 'takeaway' in stripped.lower()):
                in_key_points = True
                continue

            if in_key_points:
                # Extract bullet points or numbered items
                if stripped.startswith(('-', '*', '•')) or re.match(r'^\d+\.', stripped):
                    # Clean up the bullet/number
                    point = re.sub(r'^[-*•]\s*', '', stripped)
                    point = re.sub(r'^\d+\.\s*', '', point)
                    if point:
                        key_points.append(point)
            else:
                # Part of summary
                if stripped and not stripped.startswith('#'):
                    summary_lines.append(stripped)

        # Join summary
        summary = ' '.join(summary_lines).strip()

        # If we couldn't parse key points, take last 3-5 sentences
        if not key_points and summary:
            sentences = re.split(r'[.!?]+', summary)
            key_points = [s.strip() for s in sentences[-5:] if s.strip()]

        # Calculate word count
        word_count = len(summary.split())

        # Calculate compression ratio
        original_length = len(inputs.get('text', '').split())
        compression_ratio = round(original_length / word_count, 2) if word_count > 0 else 0

        return {
            "summary": summary,
            "key_points": key_points[:5],  # Max 5
            "word_count": word_count,
            "metadata": {
                "original_length": original_length,
                "compression_ratio": compression_ratio
            }
        }
