"""
LangChain Semantic Search Engine Package
=======================================

This package provides a complete semantic search solution with:
- PDF document processing and chunking
- Vector embeddings using sentence transformers
- PostgreSQL with pgvector for efficient vector storage
- Semantic search with similarity scoring
- RAG (Retrieval Augmented Generation) for question answering
- FastAPI web interface for easy integration

Main Components:
- document_processor: PDF processing and text chunking
- database: PostgreSQL vector storage with pgvector
- semantic_search: Embedding generation and similarity search
- rag_engine: RAG-based question answering
"""

__version__ = "1.0.0"
__author__ = "Semantic Search Engine"
__description__ = "LangChain-based semantic search engine with PostgreSQL and free embeddings"

# Import main classes for easy access
from .document_processor import DocumentProcessor, DocumentChunk
from .database import DatabaseManager, Document, DocumentChunk as DBDocumentChunk
from .semantic_search import SemanticSearchEngine
from .rag_engine import RAGEngine

__all__ = [
    "DocumentProcessor",
    "DocumentChunk", 
    "DatabaseManager",
    "Document",
    "DBDocumentChunk",
    "SemanticSearchEngine",
    "RAGEngine"
]