"""
RAG (Retrieval Augmented Generation) Engine
===========================================

This module implements RAG functionality for question answering using:
- Semantic search for relevant context retrieval
- Ollama local language models for text generation
- Context-aware prompt engineering for accurate responses
- Confidence scoring and answer validation

RAG combines the power of:
1. Retrieval: Finding relevant documents via semantic search
2. Generation: Creating comprehensive answers using Ollama models
"""

import os
from typing import List, Dict, Any, Optional
import time

from .semantic_search import SemanticSearchEngine
from .ollama_client import OllamaClient

class RAGEngine:
    """
    RAG engine that combines semantic search with Ollama text generation
    
    This class provides:
    - Context retrieval from document database
    - Prompt engineering for better responses
    - Answer generation using Ollama local models
    - Response quality assessment and confidence scoring
    """
    
    def __init__(self, 
                 search_engine: SemanticSearchEngine,
                 ollama_client: OllamaClient = None,
                 max_context_length: int = 2048,
                 temperature: float = 0.7):
        """
        Initialize the RAG engine
        
        Args:
            search_engine: Initialized semantic search engine
            ollama_client: Ollama client for text generation
            max_context_length: Maximum length of context to include
            temperature: Sampling temperature for text generation (0.0 = deterministic)
        """
        self.search_engine = search_engine
        self.ollama_client = ollama_client or OllamaClient()
        
        self.max_context_length = max_context_length
        self.temperature = temperature
        
        # Performance tracking
        self.generation_stats = {
            "total_queries": 0,
            "average_generation_time": 0.0,
            "average_context_length": 0.0
        }
        
        print(f"🔧 RAG Engine initialized with Ollama client")
    
    def initialize(self):
        """
        Initialize the Ollama client and check model availability
        
        This method verifies that Ollama is running and the model is available.
        """
        try:
            print(f"🔄 Checking Ollama connection and model availability...")
            
            # Check if Ollama server is healthy
            if not self.ollama_client.health_check():
                raise Exception("Ollama server is not running. Please start Ollama first.")
            
            # Check if the default model is available
            if not self.ollama_client.check_model_available():
                print(f"🔄 Model {self.ollama_client.model_name} not found. Attempting to pull...")
                if not self.ollama_client.pull_model(self.ollama_client.model_name):
                    raise Exception(f"Failed to pull model {self.ollama_client.model_name}")
            
            print("✅ Ollama client initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing Ollama client: {str(e)}")
            raise e
    
    
    def generate_answer(self, 
                            question: str, 
                            top_k: int = 3,
                            max_tokens: int = 512,
                            include_sources: bool = True) -> Dict[str, Any]:
        """
        Generate an answer to a question using RAG
        
        This method:
        1. Retrieves relevant context using semantic search
        2. Constructs a prompt with question and context
        3. Generates an answer using the language model
        4. Calculates confidence score based on context relevance
        
        Args:
            question: The question to answer
            top_k: Number of context chunks to retrieve
            max_tokens: Maximum tokens in generated response
            include_sources: Whether to include source documents in response
            
        Returns:
            Dict containing:
                - answer: Generated answer text
                - source_documents: List of source chunks used
                - confidence_score: Confidence in the answer (0-1)
                - generation_time: Time taken to generate answer
                
        Raises:
            Exception: If generation fails
        """
        try:
            start_time = time.time()
            self.generation_stats["total_queries"] += 1
            
            # Step 1: Retrieve relevant context
            print(f"🔍 Retrieving context for question: {question[:100]}...")
            
            search_results = self.search_engine.search(
                query=question,
                top_k=top_k,
                similarity_threshold=0.6  # Lower threshold for more context
            )
            
            if not search_results:
                return {
                    "answer": "I couldn't find any relevant information to answer your question. Please try rephrasing or check if the relevant documents have been uploaded.",
                    "source_documents": [],
                    "confidence_score": 0.0,
                    "generation_time": time.time() - start_time
                }
            
            # Step 2: Prepare context
            context = self._prepare_context(search_results)
            
            # Step 3: Generate answer using Ollama
            try:
                answer = self.ollama_client.generate_with_context(
                    question=question,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=self.temperature
                )
            except Exception as e:
                print(f"⚠️  Ollama generation failed: {str(e)}")
                # Fallback to template-based answer
                answer = self._generate_template_answer(question, search_results)
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence_score(search_results, answer)
            
            # Update statistics
            generation_time = time.time() - start_time
            self._update_generation_stats(generation_time, len(context))
            
            print(f"✅ Generated answer in {generation_time:.2f}s (confidence: {confidence_score:.2f})")
            
            result = {
                "answer": answer,
                "confidence_score": confidence_score,
                "generation_time": generation_time
            }
            
            if include_sources:
                result["source_documents"] = search_results
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating RAG answer: {str(e)}")
            raise e
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Prepare context text from search results
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            str: Formatted context text for prompt
        """
        context_parts = []
        
        for i, result in enumerate(search_results):
            # Extract metadata for source attribution
            filename = result["metadata"].get("filename", "Unknown")
            chunk_idx = result["metadata"].get("chunk_index", i)
            
            # Format context chunk with source information
            context_part = f"Source {i+1} (from {filename}, section {chunk_idx}):\n{result['content']}\n"
            context_parts.append(context_part)
        
        context = "\n".join(context_parts)
        
        # Truncate context if it's too long
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "...[truncated]"
        
        return context
    
    
    
    def _generate_template_answer(self, question: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Generate a template-based answer when model generation is unavailable
        
        Args:
            question: User's question
            search_results: Retrieved context documents
            
        Returns:
            str: Template-based answer
        """
        if not search_results:
            return "I couldn't find relevant information to answer your question."
        
        # Create a simple extractive answer from the most relevant result
        best_result = search_results[0]
        filename = best_result["metadata"].get("filename", "the document")
        
        answer = f"Based on the information from {filename}, here's what I found:\n\n"
        answer += best_result["content"][:500]  # Limit length
        
        if len(search_results) > 1:
            answer += f"\n\nAdditional relevant information was found in {len(search_results) - 1} other sections."
        
        return answer
    
    
    def _calculate_confidence_score(self, 
                                  search_results: List[Dict[str, Any]], 
                                  answer: str) -> float:
        """
        Calculate confidence score for the generated answer
        
        Args:
            search_results: Retrieved context documents
            answer: Generated answer text
            
        Returns:
            float: Confidence score between 0 and 1
        """
        if not search_results:
            return 0.0
        
        # Base confidence on search result similarity scores
        similarity_scores = [result["similarity_score"] for result in search_results]
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        
        # Adjust confidence based on number of supporting documents
        document_confidence = min(len(search_results) / 3.0, 1.0)
        
        # Adjust confidence based on answer length (very short answers are less confident)
        length_confidence = min(len(answer) / 100.0, 1.0)
        
        # Combine factors for overall confidence
        confidence = (avg_similarity * 0.6 + document_confidence * 0.2 + length_confidence * 0.2)
        
        return round(min(confidence, 1.0), 3)
    
    def _update_generation_stats(self, generation_time: float, context_length: int):
        """
        Update performance statistics
        
        Args:
            generation_time: Time taken for this generation
            context_length: Length of context used
        """
        total_queries = self.generation_stats["total_queries"]
        
        # Update average generation time
        self.generation_stats["average_generation_time"] = (
            (self.generation_stats["average_generation_time"] * (total_queries - 1) + generation_time)
            / total_queries
        )
        
        # Update average context length
        self.generation_stats["average_context_length"] = (
            (self.generation_stats["average_context_length"] * (total_queries - 1) + context_length)
            / total_queries
        )
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """
        Get RAG performance statistics
        
        Returns:
            Dict: Generation statistics and model information
        """
        return {
            "total_queries": self.generation_stats["total_queries"],
            "average_generation_time_seconds": round(self.generation_stats["average_generation_time"], 3),
            "average_context_length": round(self.generation_stats["average_context_length"], 1),
            "ollama_model": self.ollama_client.model_name,
            "ollama_url": self.ollama_client.base_url,
            "max_context_length": self.max_context_length,
            "temperature": self.temperature,
            "ollama_healthy": self.ollama_client.health_check(),
            "model_available": self.ollama_client.check_model_available()
        }