"""
OpenAI RAG Agent - Uses OpenAI ChatCompletions with retrieval
Handles question answering with citations from the textbook
"""

from typing import List, Dict, Optional
from openai import OpenAI

class OpenAIRAGAgent:
    def __init__(self, api_key: str, rag_engine):
        """
        Initialize OpenAI Agent with RAG capabilities
        """
        self.client = OpenAI(api_key=api_key)
        self.rag_engine = rag_engine
        self.model = "gpt-4o-mini"

        self.system_prompt = """You are an expert AI teaching assistant for the Physical AI & Humanoid Robotics textbook.

Your role is to:
1. Answer questions clearly and accurately based on the textbook content
2. Provide detailed explanations with examples when needed
3. Reference specific chapters and sections when citing information
4. Help students understand complex concepts in robotics and AI
5. Suggest related topics for deeper learning

Guidelines:
- Base your answers on the provided context from the textbook
- If the context doesn't contain enough information, say so honestly
- Use clear, educational language appropriate for students
- Include relevant code examples or mathematical formulas when helpful
- Encourage hands-on practice and experimentation

Always cite your sources using the chapter and section information provided in the context."""

    async def ask(self, question: str, chapter: Optional[str] = None, user_id: str = "anonymous") -> Dict:
        """
        Ask a question and get AI-generated answer with RAG
        """
        # Retrieve relevant context
        relevant_docs = await self.rag_engine.query(
            question=question,
            top_k=5,
            chapter=chapter
        )

        # Build context from retrieved documents
        context_parts = []
        sources = []

        for idx, doc in enumerate(relevant_docs):
            context_parts.append(
                f"[Source {idx+1}] From {doc['metadata'].get('title', 'Unknown')}:\n{doc['text']}"
            )
            sources.append({
                'title': doc['metadata'].get('title', 'Unknown'),
                'chapter': doc['metadata'].get('chapter', 'Unknown'),
                'file_path': doc['metadata'].get('file_path', ''),
                'relevance_score': doc['score'],
                'excerpt': doc['text'][:200] + "..."
            })

        context = "\n\n".join(context_parts)

        # Build messages for ChatCompletion
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Based on the following context from the Physical AI textbook, please answer this question:

Question: {question}

Context:
{context}

Please provide a comprehensive answer with references to the relevant chapters/sections."""}
        ]

        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content

        return {
            'answer': answer,
            'sources': sources,
            'question': question
        }

    async def ask_selected(self, selected_text: str, question: str, user_id: str = "anonymous") -> Dict:
        """
        Ask a question about specifically selected text
        """
        # Build focused context
        context = f"""Selected Text from Textbook:
{selected_text}

Question about this text: {question}"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]

        # Get response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        answer = response.choices[0].message.content

        return {
            'answer': answer,
            'sources': [{'type': 'selected_text', 'content': selected_text[:500]}],
            'question': question
        }

    async def generate_quiz(self, chapter: str) -> Dict:
        """
        Generate a quiz for a specific chapter
        """
        # Get chapter content
        relevant_docs = await self.rag_engine.query(
            question=f"Content from {chapter}",
            top_k=10,
            chapter=chapter
        )

        # Build context
        context = "\n".join([doc['text'] for doc in relevant_docs])

        messages = [
            {"role": "system", "content": "You are a quiz generator for a robotics textbook. Create challenging but fair multiple-choice questions."},
            {"role": "user", "content": f"""Based on this chapter content, create 5 multiple-choice questions:

{context}

Format each question as:
Q: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Correct: [A/B/C/D]
Explanation: [why this is correct]"""}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8,
            max_tokens=1500
        )

        quiz_content = response.choices[0].message.content

        return {
            'quiz': quiz_content,
            'chapter': chapter
        }

    async def explain_concept(self, concept: str, difficulty: str = "intermediate") -> Dict:
        """
        Explain a concept at specified difficulty level
        """
        # Retrieve relevant information
        relevant_docs = await self.rag_engine.query(
            question=concept,
            top_k=3
        )

        context = "\n".join([doc['text'] for doc in relevant_docs])

        difficulty_prompts = {
            'beginner': "Explain this in simple terms suitable for someone new to robotics.",
            'intermediate': "Provide a detailed explanation with technical details.",
            'expert': "Provide an advanced, comprehensive explanation with mathematical rigor."
        }

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Concept: {concept}

Context from textbook:
{context}

{difficulty_prompts.get(difficulty, difficulty_prompts['intermediate'])}

Include:
1. Clear definition
2. Practical examples
3. Common applications in robotics
4. Related concepts to explore"""}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1200
        )

        explanation = response.choices[0].message.content

        return {
            'explanation': explanation,
            'concept': concept,
            'difficulty': difficulty,
            'sources': [doc['metadata'] for doc in relevant_docs]
        }
