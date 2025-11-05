"""
RAG (Retrieval Augmented Generation) Engine
===========================================

This module implements RAG functionality for question answering using:
- Semantic search for relevant context retrieval
- Free language models from Hugging Face for text generation
- Context-aware prompt engineering for accurate responses
- Confidence scoring and answer validation

RAG combines the power of:
1. Retrieval: Finding relevant documents via semantic search
2. Generation: Creating comprehensive answers using retrieved context
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import time

from .semantic_search import SemanticSearchEngine

class RAGEngine:
    """
    RAG engine that combines semantic search with text generation
    
    This class provides:
    - Context retrieval from document database
    - Prompt engineering for better responses
    - Answer generation using free language models
    - Response quality assessment and confidence scoring
    """
    
    def __init__(self, 
                 search_engine: SemanticSearchEngine,
                 model_name: str = None,
                 max_context_length: int = 2048,
                 temperature: float = 0.7):
        """
        Initialize the RAG engine
        
        Args:
            search_engine: Initialized semantic search engine
            model_name: Name of the language model to use for generation
            max_context_length: Maximum length of context to include
            temperature: Sampling temperature for text generation (0.0 = deterministic)
        """
        self.search_engine = search_engine
        
        # Use model from environment or default to a free, capable model
        self.model_name = model_name or os.getenv("LLM_MODEL", "microsoft/DialoGPT-medium")
        
        self.max_context_length = max_context_length
        self.temperature = temperature
        
        # Model components (initialized lazily)
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForCausalLM] = None
        self.generator: Optional[pipeline] = None
        
        # Performance tracking
        self.generation_stats = {
            "total_queries": 0,
            "average_generation_time": 0.0,
            "average_context_length": 0.0
        }
        
        # Check for GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 RAG Engine will use device: {self.device}")
    
    async def initialize(self):
        """
        Initialize the language model and tokenizer
        
        This method loads the model components for text generation.
        Models are downloaded on first use.
        """
        try:
            print(f"🔄 Loading language model: {self.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                padding_side="left"  # Important for batch generation
            )
            
            # Add pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate settings
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                do_sample=True,
                temperature=self.temperature,
                max_new_tokens=512,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("✅ Language model loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading language model: {str(e)}")
            # Fallback to a simpler approach for text generation
            print("🔄 Falling back to simple text generation...")
            await self._initialize_fallback_generator()
    
    async def _initialize_fallback_generator(self):
        """
        Initialize a fallback text generator for when full models fail to load
        
        This provides basic functionality using smaller, more reliable models.
        """
        try:
            # Use a smaller, more reliable model for fallback
            fallback_model = "gpt2"
            
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.generator = pipeline(
                "text-generation",
                model=fallback_model,
                tokenizer=self.tokenizer,
                device=-1,  # Force CPU for reliability
                max_new_tokens=256,
                do_sample=True,
                temperature=0.8,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("✅ Fallback text generator initialized")
            
        except Exception as e:
            print(f"❌ Error initializing fallback generator: {str(e)}")
            self.generator = None
    
    async def generate_answer(self, 
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
            
            search_results = await self.search_engine.search(
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
            
            # Step 2: Prepare context and prompt
            context = self._prepare_context(search_results)
            prompt = self._construct_prompt(question, context)
            
            # Step 3: Generate answer
            if self.generator is None:
                # Fallback to template-based response if no generator available
                answer = self._generate_template_answer(question, search_results)
            else:
                answer = await self._generate_model_answer(prompt, max_tokens)
            
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
    
    def _construct_prompt(self, question: str, context: str) -> str:
        """
        Construct a well-formatted prompt for the language model
        
        Args:
            question: User's question
            context: Retrieved context text
            
        Returns:
            str: Formatted prompt for text generation
        """
        prompt = f"""Context Information:
{context}

Question: {question}

Based on the context information provided above, please provide a comprehensive and accurate answer to the question. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing.

Answer:"""
        
        return prompt
    
    async def _generate_model_answer(self, prompt: str, max_tokens: int) -> str:
        """
        Generate answer using the language model
        
        Args:
            prompt: Formatted prompt with context and question
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated answer text
        """
        try:
            # Generate response using the pipeline
            response = self.generator(
                prompt,
                max_new_tokens=min(max_tokens, 512),
                num_return_sequences=1,
                truncation=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text (remove the original prompt)
            generated_text = response[0]["generated_text"]
            answer = generated_text[len(prompt):].strip()
            
            # Clean up the answer
            answer = self._clean_generated_answer(answer)
            
            return answer
            
        except Exception as e:
            print(f"⚠️  Model generation failed: {str(e)}")
            # Fallback to template-based answer
            return "I apologize, but I encountered an issue generating a response. Please try again."
    
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
    
    def _clean_generated_answer(self, answer: str) -> str:
        """
        Clean and format generated answer text
        
        Args:
            answer: Raw generated answer
            
        Returns:
            str: Cleaned answer text
        """
        # Remove common generation artifacts
        answer = answer.replace("<|endoftext|>", "")
        answer = answer.replace("[PAD]", "")
        
        # Remove excessive whitespace
        lines = [line.strip() for line in answer.split('\n')]
        answer = '\n'.join(line for line in lines if line)
        
        # Limit answer length if too verbose
        if len(answer) > 1000:
            # Find a good breaking point (end of sentence)
            break_point = answer.rfind('.', 0, 900)
            if break_point > 500:
                answer = answer[:break_point + 1]
        
        return answer.strip()
    
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
            "model_name": self.model_name,
            "device": self.device,
            "max_context_length": self.max_context_length,
            "temperature": self.temperature,
            "model_loaded": self.generator is not None
        }