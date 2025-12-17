"""
Text Splitter - Splits long documents into chunks for embedding
Maintains context with overlapping chunks
"""

import re
from typing import List, Dict

class TextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text splitter
        chunk_size: Maximum characters per chunk
        chunk_overlap: Characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        Tries to split on paragraph boundaries
        """
        # First, split on double newlines (paragraphs)
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                    # Start new chunk with overlap
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    # Paragraph itself is too long, split it
                    chunks.extend(self._split_long_text(paragraph))
                    current_chunk = ""
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_long_text(self, text: str) -> List[str]:
        """
        Split very long text (e.g., long paragraph or code block)
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to find a sentence boundary
            if end < len(text):
                # Look for sentence end within last 100 characters
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - self.chunk_overlap

        return chunks

    def split_by_section(self, text: str) -> List[Dict]:
        """
        Split text by markdown sections (##, ###, etc.)
        Preserves section hierarchy
        """
        sections = []
        current_section = {
            'level': 0,
            'title': '',
            'content': ''
        }

        for line in text.split('\n'):
            # Check if line is a heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if heading_match:
                # Save previous section
                if current_section['content']:
                    sections.append(current_section)

                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2)

                current_section = {
                    'level': level,
                    'title': title,
                    'content': line + '\n'
                }
            else:
                current_section['content'] += line + '\n'

        # Add last section
        if current_section['content']:
            sections.append(current_section)

        return sections
