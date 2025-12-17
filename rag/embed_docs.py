"""
Script to embed all documents into Qdrant
Run this after initial setup to populate the vector database
"""

import asyncio
import os
from dotenv import load_dotenv
from api.rag_engine import RAGEngine

load_dotenv()

async def main():
    print("Starting document embedding process...")

    # Initialize RAG engine
    rag_engine = RAGEngine(
        qdrant_url=os.getenv("QDRANT_URL"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # Embed all documents
    docs_path = "../docs"  # Adjust path as needed

    print(f"Loading documents from: {docs_path}")
    result = await rag_engine.embed_all_documents(docs_path)

    print("\n=== Embedding Complete ===")
    print(f"Documents processed: {result['num_documents']}")
    print(f"Chunks created: {result['num_chunks']}")
    print(f"Status: {result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
