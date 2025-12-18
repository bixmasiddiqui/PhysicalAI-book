"""
RAG Engine - Handles document embedding and retrieval
Integrates with Qdrant for vector storage and OpenAI for embeddings
"""

import os
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
import hashlib

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.document_loader import DocumentLoader
from utils.text_splitter import TextSplitter

class RAGEngine:
    def __init__(self, qdrant_url: str, qdrant_api_key: str, openai_api_key: str):
        """
        Initialize RAG engine with Qdrant and OpenAI
        """
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
        )
        self.openai_client = OpenAI(api_key=openai_api_key)

        self.collection_name = "physical_ai_textbook"
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536

        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection: {e}")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI"""
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding

    async def embed_all_documents(self, docs_path: str) -> Dict:
        """
        Load and embed all documents from the docs folder
        """
        # Load documents
        loader = DocumentLoader(docs_path)
        documents = loader.load_all_markdown()

        # Split into chunks
        splitter = TextSplitter(chunk_size=1000, chunk_overlap=200)

        all_chunks = []
        for doc in documents:
            chunks = splitter.split_text(doc['content'])
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'metadata': {
                        **doc['metadata'],
                        'chunk_id': i,
                        'total_chunks': len(chunks)
                    }
                })

        print(f"Processing {len(all_chunks)} chunks from {len(documents)} documents")

        # Embed and upload to Qdrant
        points = []
        for idx, chunk in enumerate(all_chunks):
            # Get embedding
            embedding = self.get_embedding(chunk['text'])

            # Create unique ID
            chunk_id = hashlib.md5(
                f"{chunk['metadata']['file_path']}_{chunk['metadata']['chunk_id']}".encode()
            ).hexdigest()

            # Create point
            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    'text': chunk['text'],
                    'file_path': chunk['metadata']['file_path'],
                    'title': chunk['metadata'].get('title', ''),
                    'chapter': chunk['metadata'].get('chapter', ''),
                    'chunk_id': chunk['metadata']['chunk_id']
                }
            )
            points.append(point)

            # Upload in batches of 100
            if len(points) >= 100:
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                points = []
                print(f"Uploaded {idx + 1}/{len(all_chunks)} chunks")

        # Upload remaining points
        if points:
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )

        return {
            'num_documents': len(documents),
            'num_chunks': len(all_chunks),
            'status': 'success'
        }

    async def query(self, question: str, top_k: int = 5, chapter: str = None) -> List[Dict]:
        """
        Query vector database for relevant chunks
        """
        # Get embedding for question
        query_embedding = self.get_embedding(question)

        # Build filter if chapter specified
        query_filter = None
        if chapter:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="chapter",
                        match=MatchValue(value=chapter)
                    )
                ]
            )

        # Search
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter
        )

        # Format results
        results = []
        for hit in search_result:
            results.append({
                'text': hit.payload['text'],
                'score': hit.score,
                'metadata': {
                    'file_path': hit.payload.get('file_path'),
                    'title': hit.payload.get('title'),
                    'chapter': hit.payload.get('chapter'),
                    'chunk_id': hit.payload.get('chunk_id')
                }
            })

        return results

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Simple search without AI response generation
        """
        return await self.query(query, top_k)
