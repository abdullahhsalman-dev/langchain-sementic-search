"""
Semantic Search Engine Module
=============================

This module implements the core semantic search functionality using:
- Sentence Transformers for free, high-quality embeddings
- PostgreSQL with pgvector for vector storage and similarity search
- Efficient caching and batch processing for performance

Provides methods for:
- Text embedding generation
- Document chunk storage with vectors
- Semantic similarity search
- Search result ranking and filtering
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import time

from .database import DatabaseManager
from .document_processor import DocumentChunk

class SemanticSearchEngine:
    """
    Core semantic search engine that handles embedding generation and vector search
    
    This class manages:
    - Loading and using sentence transformer models
    - Generating embeddings for text content
    - Storing document chunks with vector embeddings
    - Performing semantic similarity searches
    - Caching and performance optimization
    """
    
    def __init__(self, 
                 model_name: str = None,
                 database_url: str = None,
                 cache_embeddings: bool = True):
        """
        Initialize the semantic search engine
        
        Args:
            model_name: Name of sentence transformer model to use
            database_url: PostgreSQL connection URL
            cache_embeddings: Whether to cache embeddings for repeated queries
        """
        # Use model from environment or default to efficient multilingual model
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Initialize model (will download on first use)
        self.model: Optional[SentenceTransformer] = None
        self.embedding_dimension: Optional[int] = None
        
        # Database manager for vector storage
        self.db_manager = DatabaseManager(database_url)
        
        # Embedding cache for performance optimization
        self.cache_embeddings = cache_embeddings
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "average_search_time": 0.0
        }
    
    def initialize(self):
        """
        Initialize the search engine components
        
        This method:
        1. Loads the sentence transformer model
        2. Initializes the database connection
        3. Sets up vector dimensions and indexes
        4. Performs initial health checks
        
        Should be called once during application startup.
        """
        try:
            print(f"🔄 Loading embedding model: {self.model_name}")
            
            # Load sentence transformer model
            # This will download the model on first use (~90MB for all-MiniLM-L6-v2)
            self.model = SentenceTransformer(self.model_name)
            
            # Get embedding dimension from a test encoding
            test_embedding = self.model.encode(["test"], convert_to_numpy=True)
            self.embedding_dimension = test_embedding.shape[1]
            
            print(f"✅ Model loaded. Embedding dimension: {self.embedding_dimension}")
            
            # Initialize database
            self.db_manager.initialize_database()
            
            print("✅ Semantic search engine initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing semantic search engine: {str(e)}")
            raise e
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate vector embedding for input text
        
        Args:
            text: Input text to embed
            
        Returns:
            np.ndarray: Vector embedding of specified dimension
            
        Raises:
            Exception: If model is not initialized or encoding fails
        """
        if not self.model:
            raise Exception("Model not initialized. Call initialize() first.")
        
        # Check cache first if enabled
        if self.cache_embeddings and text in self.embedding_cache:
            self.search_stats["cache_hits"] += 1
            return self.embedding_cache[text]
        
        try:
            # Generate embedding using sentence transformer
            # convert_to_numpy=True ensures we get numpy array
            embedding = self.model.encode([text], convert_to_numpy=True)[0]
            
            # Cache the embedding if caching is enabled
            if self.cache_embeddings:
                self.embedding_cache[text] = embedding
                
                # Limit cache size to prevent memory issues
                if len(self.embedding_cache) > 1000:
                    # Remove oldest entries (simple FIFO)
                    oldest_key = next(iter(self.embedding_cache))
                    del self.embedding_cache[oldest_key]
            
            return embedding
            
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently
        
        Batch processing is more efficient than individual calls for large datasets.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List[np.ndarray]: List of vector embeddings
            
        Raises:
            Exception: If model is not initialized or batch encoding fails
        """
        if not self.model:
            raise Exception("Model not initialized. Call initialize() first.")
        
        try:
            # Check which texts are already cached
            uncached_texts = []
            uncached_indices = []
            cached_embeddings = {}
            
            if self.cache_embeddings:
                for i, text in enumerate(texts):
                    if text in self.embedding_cache:
                        cached_embeddings[i] = self.embedding_cache[text]
                        self.search_stats["cache_hits"] += 1
                    else:
                        uncached_texts.append(text)
                        uncached_indices.append(i)
            else:
                uncached_texts = texts
                uncached_indices = list(range(len(texts)))
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                batch_embeddings = self.model.encode(uncached_texts, convert_to_numpy=True)
                
                # Cache new embeddings
                if self.cache_embeddings:
                    for text, embedding in zip(uncached_texts, batch_embeddings):
                        self.embedding_cache[text] = embedding
            else:
                batch_embeddings = []
            
            # Combine cached and new embeddings in correct order
            result_embeddings = [None] * len(texts)
            
            # Fill in cached embeddings
            for i, embedding in cached_embeddings.items():
                result_embeddings[i] = embedding
            
            # Fill in new embeddings
            for i, batch_idx in enumerate(uncached_indices):
                result_embeddings[batch_idx] = batch_embeddings[i]
            
            return result_embeddings
            
        except Exception as e:
            raise Exception(f"Error generating batch embeddings: {str(e)}")
    
    def store_document_chunks(self, 
                                  chunks: List[DocumentChunk], 
                                  metadata: Dict[str, Any]) -> int:
        """
        Store document chunks with their vector embeddings
        
        This method:
        1. Generates embeddings for all chunk content
        2. Stores document metadata
        3. Stores chunks with embeddings in the vector database
        
        Args:
            chunks: List of DocumentChunk objects to store
            metadata: Document-level metadata
            
        Returns:
            int: Number of chunks successfully stored
            
        Raises:
            Exception: If storage fails
        """
        try:
            start_time = time.time()
            
            # Extract text content for batch embedding generation
            chunk_texts = [chunk.content for chunk in chunks]
            
            print(f"🔄 Generating embeddings for {len(chunk_texts)} chunks...")
            
            # Generate embeddings in batch for efficiency
            embeddings = self.generate_batch_embeddings(chunk_texts)
            
            # Store document metadata first
            document_id = chunks[0].metadata["document_id"]
            self.db_manager.store_document(document_id, metadata)
            
            # Prepare chunk data for database storage
            chunk_data = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_data.append({
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.metadata["document_id"],
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "embedding": embedding.tolist(),  # Convert numpy array to list for JSON
                    "metadata": chunk.metadata
                })
            
            # Store chunks in database
            stored_count = self.db_manager.store_chunks(chunk_data)
            
            processing_time = time.time() - start_time
            print(f"✅ Stored {stored_count} chunks with embeddings in {processing_time:.2f}s")
            
            return stored_count
            
        except Exception as e:
            print(f"❌ Error storing document chunks: {str(e)}")
            raise e
    
    def search(self, 
                    query: str, 
                    top_k: int = 5,
                    similarity_threshold: float = 0.7,
                    document_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search for the given query
        
        This method:
        1. Generates embedding for the search query
        2. Performs vector similarity search in database
        3. Ranks and filters results
        4. Returns formatted search results
        
        Args:
            query: Search query text
            top_k: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            document_filter: Optional document ID to filter results
            
        Returns:
            List of search result dictionaries containing:
                - content: Matching text content
                - similarity_score: Cosine similarity score
                - metadata: Chunk and document metadata
                - chunk_id: Unique chunk identifier
                
        Raises:
            Exception: If search fails
        """
        try:
            start_time = time.time()
            self.search_stats["total_searches"] += 1
            
            # Generate embedding for search query
            query_embedding = self.generate_embedding(query)
            
            # Perform vector similarity search
            results = self.db_manager.similarity_search(
                query_embedding=query_embedding.tolist(),
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # Apply document filter if specified
            if document_filter:
                results = [r for r in results if r["metadata"].get("document_id") == document_filter]
            
            # Update performance statistics
            search_time = time.time() - start_time
            self.search_stats["average_search_time"] = (
                (self.search_stats["average_search_time"] * (self.search_stats["total_searches"] - 1) + search_time)
                / self.search_stats["total_searches"]
            )
            
            print(f"🔍 Found {len(results)} results in {search_time:.3f}s")
            
            return results
            
        except Exception as e:
            print(f"❌ Error performing search: {str(e)}")
            raise e
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all stored documents
        
        Returns:
            List of document metadata dictionaries
        """
        try:
            return self.db_manager.get_all_documents()
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its associated chunks
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            bool: True if document was deleted successfully
        """
        try:
            return self.db_manager.delete_document(document_id)
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check health of search engine components
        
        Returns:
            bool: True if all components are healthy
        """
        try:
            # Check model is loaded
            if not self.model:
                return False
            
            # Check database connectivity
            db_healthy = self.db_manager.health_check()
            
            # Test embedding generation
            try:
                test_embedding = self.generate_embedding("health check")
                embedding_healthy = len(test_embedding) == self.embedding_dimension
            except:
                embedding_healthy = False
            
            return db_healthy and embedding_healthy
            
        except Exception:
            return False
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get search performance statistics
        
        Returns:
            Dict: Search statistics including cache performance and timing
        """
        cache_hit_rate = (
            self.search_stats["cache_hits"] / max(1, self.search_stats["total_searches"])
        ) * 100
        
        return {
            "total_searches": self.search_stats["total_searches"],
            "cache_hits": self.search_stats["cache_hits"],
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "average_search_time_seconds": round(self.search_stats["average_search_time"], 3),
            "embedding_cache_size": len(self.embedding_cache),
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension
        }
    
    def clear_cache(self):
        """Clear the embedding cache to free memory"""
        self.embedding_cache.clear()
        print("🧹 Embedding cache cleared")