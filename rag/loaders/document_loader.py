"""
Document Loader - Loads markdown files from docs folder
Extracts metadata and content for embedding
"""

import os
from typing import List, Dict
import re

class DocumentLoader:
    def __init__(self, docs_path: str):
        """
        Initialize document loader
        docs_path: Path to docs folder
        """
        self.docs_path = docs_path

    def load_all_markdown(self) -> List[Dict]:
        """
        Load all markdown files from docs folder
        """
        documents = []

        for root, dirs, files in os.walk(self.docs_path):
            for file in files:
                if file.endswith('.md') or file.endswith('.mdx'):
                    file_path = os.path.join(root, file)
                    doc = self.load_markdown_file(file_path)
                    if doc:
                        documents.append(doc)

        return documents

    def load_markdown_file(self, file_path: str) -> Dict:
        """
        Load a single markdown file and extract metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter metadata
            metadata = self.extract_frontmatter(content)

            # Remove frontmatter from content
            content_without_frontmatter = self.remove_frontmatter(content)

            # Extract title if not in metadata
            if 'title' not in metadata:
                title_match = re.search(r'^#\s+(.+)$', content_without_frontmatter, re.MULTILINE)
                if title_match:
                    metadata['title'] = title_match.group(1)

            # Extract chapter number from filename or content
            chapter_match = re.search(r'chapter-(\d+)', file_path.lower())
            if chapter_match:
                metadata['chapter'] = f"Chapter {chapter_match.group(1)}"

            return {
                'content': content_without_frontmatter,
                'metadata': {
                    **metadata,
                    'file_path': file_path,
                    'filename': os.path.basename(file_path)
                }
            }

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def extract_frontmatter(self, content: str) -> Dict:
        """
        Extract YAML frontmatter from markdown
        """
        metadata = {}

        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)

            # Parse simple key: value pairs
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

        return metadata

    def remove_frontmatter(self, content: str) -> str:
        """
        Remove YAML frontmatter from content
        """
        return re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
