"""
Database Module for Vector Storage
==================================

This module handles PostgreSQL database operations with pgvector extension for:
- Vector storage and similarity search
- Document and chunk metadata management
- Database connection and session management
- Vector indexing for performance optimization

Uses SQLAlchemy for ORM and pgvector for vector operations.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import numpy as np

from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

# Create base class for SQLAlchemy models
Base = declarative_base()

class Document(Base):
    """
    SQLAlchemy model for document metadata
    
    Stores information about uploaded documents including:
    - Document identification and metadata
    - Processing statistics
    - Upload and processing timestamps
    """
    __tablename__ = "documents"
    
    # Primary key - unique document identifier
    id = Column(String, primary_key=True)
    
    # Document metadata
    filename = Column(String, nullable=False)
    file_type = Column(String, default="pdf")
    file_size_bytes = Column(Integer)
    
    # Content statistics
    content_length = Column(Integer)
    word_count = Column(Integer)
    total_chunks = Column(Integer)
    
    # Processing configuration
    chunk_size = Column(Integer)
    chunk_overlap = Column(Integer)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Additional metadata as JSON
    metadata = Column(JSON)

class DocumentChunk(Base):
    """
    SQLAlchemy model for document chunks with vector embeddings
    
    Stores:
    - Text content and metadata for each chunk
    - Vector embeddings for semantic search
    - Relationships to parent documents
    """
    __tablename__ = "document_chunks"
    
    # Primary key - unique chunk identifier
    id = Column(String, primary_key=True)
    
    # Foreign key to parent document
    document_id = Column(String, nullable=False)
    
    # Chunk content and position
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # Vector embedding for semantic search
    # Dimension will be set based on the embedding model used
    embedding = Column(Vector(384))  # 384 dimensions for all-MiniLM-L6-v2
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata as JSON
    metadata = Column(JSON)

class DatabaseManager:
    """
    Manages database connections and operations for the semantic search system
    
    Handles:
    - Database initialization and connection
    - Table creation and migration
    - Session management for async operations
    - Vector index optimization
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager
        
        Args:
            database_url: PostgreSQL connection URL (defaults to env variable)
        """
        # Get database URL from environment or parameter
        self.database_url = database_url or os.getenv("DATABASE_URL")
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable must be set")
        
        # Create async engine for database operations
        # echo=True enables SQL logging for debugging (disable in production)
        self.async_engine = create_async_engine(
            self.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,  # Set to True for SQL query logging
            pool_size=10,  # Connection pool size
            max_overflow=20  # Maximum overflow connections
        )
        
        # Create async session factory
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def initialize_database(self):
        """
        Initialize database tables and pgvector extension
        
        This method:
        1. Creates the pgvector extension if it doesn't exist
        2. Creates all necessary tables
        3. Sets up vector indexes for performance
        
        Should be called once during application startup.
        """
        try:
            async with self.async_engine.begin() as conn:
                # Enable pgvector extension
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                
                # Create all tables defined in Base
                await conn.run_sync(Base.metadata.create_all)
                
                # Create vector index for efficient similarity search
                # Using HNSW (Hierarchical Navigable Small World) index for fast approximate search
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
                    ON document_chunks USING hnsw (embedding vector_cosine_ops)
                """))
                
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            raise e
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session
        
        Yields:
            AsyncSession: Database session for operations
            
        Example:
            async with database.get_session() as session:
                # Perform database operations
                pass
        """
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """
        Check database connectivity and health
        
        Returns:
            bool: True if database is accessible and healthy
        """
        try:
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
                
        except Exception as e:
            print(f"Database health check failed: {str(e)}")
            return False
    
    async def store_document(self, 
                           document_id: str, 
                           metadata: Dict[str, Any]) -> bool:
        """
        Store document metadata in the database
        
        Args:
            document_id: Unique document identifier
            metadata: Document metadata dictionary
            
        Returns:
            bool: True if stored successfully
            
        Raises:
            Exception: If storage fails
        """
        try:
            async with self.get_session() as session:
                # Create document record
                document = Document(
                    id=document_id,
                    filename=metadata.get("filename"),
                    file_type=metadata.get("file_type", "pdf"),
                    file_size_bytes=metadata.get("file_size_bytes"),
                    content_length=metadata.get("content_length"),
                    word_count=metadata.get("word_count"),
                    chunk_size=metadata.get("chunk_size"),
                    chunk_overlap=metadata.get("chunk_overlap"),
                    processed_at=datetime.fromisoformat(metadata.get("processed_at")),
                    metadata=metadata
                )
                
                session.add(document)
                await session.commit()
                
                return True
                
        except Exception as e:
            print(f"Error storing document: {str(e)}")
            raise e
    
    async def store_chunks(self, 
                          chunks: List[Dict[str, Any]]) -> int:
        """
        Store document chunks with embeddings in the database
        
        Args:
            chunks: List of chunk dictionaries containing:
                - chunk_id: Unique identifier
                - document_id: Parent document ID
                - content: Text content
                - embedding: Vector embedding
                - metadata: Additional metadata
                
        Returns:
            int: Number of chunks stored successfully
            
        Raises:
            Exception: If storage fails
        """
        try:
            async with self.get_session() as session:
                stored_count = 0
                
                for chunk_data in chunks:
                    # Create chunk record
                    chunk = DocumentChunk(
                        id=chunk_data["chunk_id"],
                        document_id=chunk_data["document_id"],
                        content=chunk_data["content"],
                        chunk_index=chunk_data.get("chunk_index", 0),
                        embedding=chunk_data["embedding"],
                        metadata=chunk_data.get("metadata", {})
                    )
                    
                    session.add(chunk)
                    stored_count += 1
                
                await session.commit()
                return stored_count
                
        except Exception as e:
            print(f"Error storing chunks: {str(e)}")
            raise e
    
    async def similarity_search(self, 
                              query_embedding: List[float], 
                              top_k: int = 5,
                              similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search
        
        Args:
            query_embedding: Query vector embedding
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of dictionaries containing:
                - content: Chunk text content
                - similarity_score: Cosine similarity score
                - metadata: Chunk metadata
                - chunk_id: Unique chunk identifier
                
        Raises:
            Exception: If search fails
        """
        try:
            async with self.get_session() as session:
                # Perform cosine similarity search using pgvector
                # Order by similarity score descending, limit to top_k
                query = text("""
                    SELECT 
                        id,
                        content,
                        metadata,
                        (1 - (embedding <=> :query_embedding)) as similarity_score
                    FROM document_chunks
                    WHERE (1 - (embedding <=> :query_embedding)) >= :threshold
                    ORDER BY embedding <=> :query_embedding
                    LIMIT :limit
                """)
                
                result = await session.execute(
                    query,
                    {
                        "query_embedding": str(query_embedding),
                        "threshold": similarity_threshold,
                        "limit": top_k
                    }
                )
                
                # Format results
                results = []
                for row in result.fetchall():
                    results.append({
                        "chunk_id": row.id,
                        "content": row.content,
                        "similarity_score": float(row.similarity_score),
                        "metadata": row.metadata or {}
                    })
                
                return results
                
        except Exception as e:
            print(f"Error performing similarity search: {str(e)}")
            raise e
    
    async def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents and their metadata
        
        Returns:
            List of document metadata dictionaries
        """
        try:
            async with self.get_session() as session:
                query = text("""
                    SELECT 
                        d.*,
                        COUNT(c.id) as chunk_count
                    FROM documents d
                    LEFT JOIN document_chunks c ON d.id = c.document_id
                    GROUP BY d.id
                    ORDER BY d.processed_at DESC
                """)
                
                result = await session.execute(query)
                
                documents = []
                for row in result.fetchall():
                    documents.append({
                        "document_id": row.id,
                        "filename": row.filename,
                        "file_size_bytes": row.file_size_bytes,
                        "word_count": row.word_count,
                        "chunk_count": row.chunk_count,
                        "processed_at": row.processed_at.isoformat() if row.processed_at else None,
                        "metadata": row.metadata or {}
                    })
                
                return documents
                
        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            raise e
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            async with self.get_session() as session:
                # Delete chunks first (foreign key constraint)
                await session.execute(
                    text("DELETE FROM document_chunks WHERE document_id = :doc_id"),
                    {"doc_id": document_id}
                )
                
                # Delete document
                result = await session.execute(
                    text("DELETE FROM documents WHERE id = :doc_id"),
                    {"doc_id": document_id}
                )
                
                await session.commit()
                
                # Return True if any rows were deleted
                return result.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
            raise e

# Global database instance
database_manager: Optional[DatabaseManager] = None

async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get database session
    
    Yields:
        AsyncSession: Database session for request handling
    """
    global database_manager
    
    if not database_manager:
        database_manager = DatabaseManager()
        await database_manager.initialize_database()
    
    async with database_manager.get_session() as session:
        yield session

# Import text function for raw SQL queries
from sqlalchemy import text