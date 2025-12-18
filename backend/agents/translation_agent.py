


"""
Translation Agent - Translates chapters to Urdu
Uses OpenAI for high-quality technical translation
"""

from openai import OpenAI
import os

class TranslationAgent:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"

    def translate_to_urdu(self, content: str, preserve_code: bool = True) -> str:
        """
        Translate content to Urdu
        preserve_code: Keep code blocks in English
        """
        system_prompt = """You are an expert translator specializing in technical and educational content translation from English to Urdu.

Guidelines:
1. Translate all English text to Urdu
2. Preserve markdown formatting (headings, lists, bold, italic)
3. Keep code blocks in English (do not translate code)
4. Keep technical terms in English with Urdu explanation in parentheses when first introduced
5. Maintain the same document structure
6. Use clear, modern Urdu suitable for technical education
7. Preserve all URLs and links
8. Keep mathematical formulas unchanged

Technical terms to handle:
- Robot -> روبوٹ (Robot)
- Sensor -> سینسر (Sensor)
- Algorithm -> الگورتھم (Algorithm)
- Programming -> پروگرامنگ (Programming)
"""

        user_prompt = f"""Translate the following robotics textbook chapter from English to Urdu:

{content}

Remember to:
- Preserve all markdown formatting
- Keep code blocks in English
- Maintain technical accuracy
- Use appropriate Urdu technical terminology
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent translation
            max_tokens=4000
        )

        translated = response.choices[0].message.content

        return translated

    def translate_chapter_file(self, input_path: str, output_path: str):
        """
        Translate a full chapter file
        """
        # Read original
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Translate
        translated = self.translate_to_urdu(content)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Write translated version
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

        return output_path

    def batch_translate_docs(self, docs_path: str, output_path: str):
        """
        Translate all markdown files in docs folder
        """
        import glob

        md_files = glob.glob(f"{docs_path}/**/*.md", recursive=True)

        translated_files = []

        for md_file in md_files:
            # Determine output path
            relative_path = os.path.relpath(md_file, docs_path)
            output_file = os.path.join(output_path, relative_path)

            print(f"Translating: {md_file}")

            try:
                self.translate_chapter_file(md_file, output_file)
                translated_files.append(output_file)
                print(f"✓ Saved to: {output_file}")
            except Exception as e:
                print(f"✗ Error translating {md_file}: {e}")

        return translated_files
