"""
Embedding Client Module
Handles embedding API calls to Ollama, OpenAI-compatible services, and SiliconFlow
"""
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import Config
from utils import setup_logging, format_timestamp
from exceptions import APIException

logger = setup_logging(Config.LOG_LEVEL)

class EmbeddingClient:
    """Embedding API Client supporting multiple providers"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 embedding_dim: int = 0):
        """
        Initialize Embedding Client
        
        Args:
            api_key: API key (optional for local models like Ollama)
            base_url: API base URL
            model: Embedding model name
            embedding_dim: Expected embedding dimension (0 = auto-detect)
        """
        self.api_key = api_key or Config.SILICONFLOW_API_KEY
        self.base_url = base_url or Config.SILICONFLOW_API_URL
        self.model = model or "qwen3-embedding:0.6b"
        self.embedding_dim = embedding_dim
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
        
        logger.info(f"Embedding Client initialized with model: {self.model}, base_url: {self.base_url}")
    
    def _is_ollama(self) -> bool:
        """Check if base_url points to Ollama"""
        if not self.base_url:
            return True
        return "ollama" in self.base_url.lower() or "localhost:11434" in self.base_url
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float representing the embedding vector
        """
        try:
            if self._is_ollama():
                return self._get_ollama_embedding(text)
            else:
                return self._get_openai_embedding(text)
                
        except Exception as e:
            logger.error(f"Embedding request failed: {e}")
            raise APIException(f"Embedding request failed: {e}")
    
    def _get_ollama_embedding(self, text: str) -> List[float]:
        """Get embedding using Ollama API"""
        try:
            url = f"{self.base_url.rstrip('/')}/api/embeddings" if self.base_url else "http://localhost:11434/api/embeddings"
            
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            logger.debug(f"Sending Ollama embedding request to {url}")
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "embedding" in result:
                embedding = result["embedding"]
                logger.debug(f"Ollama embedding received, dimension: {len(embedding)}")
                return embedding
            else:
                raise APIException("Ollama API response does not contain embedding")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            raise APIException(f"Ollama API request failed: {e}")
    
    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI-compatible API"""
        try:
            url = f"{self.base_url.rstrip('/')}/embeddings"
            
            payload = {
                "model": self.model,
                "input": text
            }
            
            logger.debug(f"Sending OpenAI embedding request to {url}")
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0]["embedding"]
                logger.debug(f"OpenAI embedding received, dimension: {len(embedding)}")
                return embedding
            else:
                raise APIException("OpenAI API response does not contain embedding")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise APIException(f"OpenAI API request failed: {e}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Failed to embed text: {e}")
                embeddings.append([])
        return embeddings
    
    def configure(self, api_key: Optional[str] = None, 
                  base_url: Optional[str] = None,
                  model: Optional[str] = None,
                  embedding_dim: int = 0):
        """
        Reconfigure the embedding client
        
        Args:
            api_key: New API key
            base_url: New base URL
            model: New model name
            embedding_dim: New embedding dimension
        """
        if api_key is not None:
            self.api_key = api_key
            if self.api_key:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.api_key}"
                })
            elif "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
        
        if base_url is not None:
            self.base_url = base_url
        
        if model is not None:
            self.model = model
        
        if embedding_dim > 0:
            self.embedding_dim = embedding_dim
        
        logger.info(f"Embedding Client reconfigured: model={self.model}, base_url={self.base_url}")