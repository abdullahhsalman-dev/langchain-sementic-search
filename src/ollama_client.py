"""
Ollama Client Module
===================

This module provides integration with Ollama for local LLM inference.
Ollama allows running language models locally without requiring API keys
or internet connectivity for inference.

Features:
- Local model inference with Ollama
- Streaming and non-streaming responses
- Model management and health checks
- Fallback to other models if needed
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
import time

class OllamaClient:
    """
    Client for interacting with Ollama API for local LLM inference
    
    This class provides methods to:
    - Generate text using local Ollama models
    - Check model availability and health
    - Handle streaming and non-streaming responses
    - Manage timeouts and error handling
    """
    
    def __init__(self, 
                 base_url: str = None,
                 model_name: str = None,
                 timeout: int = 60):
        """
        Initialize Ollama client
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model_name: Default model to use (default: llama3.1:8b)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.timeout = timeout
        
        # Remove trailing slash from base_url
        self.base_url = self.base_url.rstrip('/')
        
        print(f"🦙 Ollama client initialized: {self.base_url} (model: {self.model_name})")
    
    def health_check(self) -> bool:
        """
        Check if Ollama server is running and responsive
        
        Returns:
            bool: True if Ollama server is healthy
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama health check failed: {str(e)}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models in Ollama
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                print(f"Failed to list models: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def check_model_available(self, model_name: str = None) -> bool:
        """
        Check if a specific model is available in Ollama
        
        Args:
            model_name: Model name to check (uses default if None)
            
        Returns:
            bool: True if model is available
        """
        model = model_name or self.model_name
        models = self.list_models()
        
        for model_info in models:
            if model_info.get("name") == model:
                return True
        
        return False
    
    def generate_response(self, 
                         prompt: str,
                         model: str = None,
                         max_tokens: int = 512,
                         temperature: float = 0.7,
                         stream: bool = False) -> str:
        """
        Generate response using Ollama model
        
        Args:
            prompt: Input prompt for generation
            model: Model name to use (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to use streaming response
            
        Returns:
            str: Generated response text
            
        Raises:
            Exception: If generation fails
        """
        model_name = model or self.model_name
        
        # Prepare request payload
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                
                generation_time = time.time() - start_time
                print(f"🦙 Generated response in {generation_time:.2f}s (streaming)")
                return full_response.strip()
            
            else:
                # Handle non-streaming response
                data = response.json()
                generation_time = time.time() - start_time
                print(f"🦙 Generated response in {generation_time:.2f}s")
                return data.get('response', '').strip()
                
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out")
        except requests.exceptions.ConnectionError:
            raise Exception("Could not connect to Ollama server")
        except Exception as e:
            raise Exception(f"Ollama generation failed: {str(e)}")
    
    def generate_with_context(self,
                            question: str,
                            context: str,
                            max_tokens: int = 512,
                            temperature: float = 0.7) -> str:
        """
        Generate response with context for RAG applications
        
        Args:
            question: User's question
            context: Retrieved context information
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            str: Generated answer based on context
        """
        # Construct RAG prompt
        prompt = f"""Context Information:
{context}

Question: {question}

Based on the context information provided above, please provide a comprehensive and accurate answer to the question. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing.

Answer:"""
        
        return self.generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model to Ollama
        
        Args:
            model_name: Name of model to pull
            
        Returns:
            bool: True if pull was successful
        """
        try:
            print(f"🦙 Pulling model: {model_name}")
            
            payload = {"name": model_name}
            
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=300  # 5 minutes for model download
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully pulled model: {model_name}")
                return True
            else:
                print(f"❌ Failed to pull model: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error pulling model: {str(e)}")
            return False
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a model
        
        Args:
            model_name: Model name (uses default if None)
            
        Returns:
            Dict: Model information including size, parameters, etc.
        """
        model = model_name or self.model_name
        
        try:
            payload = {"name": model}
            
            response = requests.post(
                f"{self.base_url}/api/show",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting model info: {str(e)}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of Ollama client and server
        
        Returns:
            Dict: Status information including health, models, etc.
        """
        status = {
            "server_url": self.base_url,
            "default_model": self.model_name,
            "server_healthy": False,
            "models_available": [],
            "default_model_available": False,
            "server_info": {}
        }
        
        # Check server health
        status["server_healthy"] = self.health_check()
        
        if status["server_healthy"]:
            # Get available models
            status["models_available"] = [m.get("name", "") for m in self.list_models()]
            
            # Check if default model is available
            status["default_model_available"] = self.check_model_available()
            
            # Get model info if available
            if status["default_model_available"]:
                status["server_info"] = self.get_model_info()
        
        return status