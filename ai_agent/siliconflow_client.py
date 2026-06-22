"""
SiliconFlow API Client Module
Handles API calls to SiliconFlow for AI model interactions
"""
import requests
import json
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime

from config import Config
from utils import setup_logging, format_timestamp, sanitize_text, truncate_text
from exceptions import APIException

logger = setup_logging(Config.LOG_LEVEL)

class SiliconFlowClient:
    """SiliconFlow API Client"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None,
                 model: Optional[str] = None):
        """
        Initialize SiliconFlow Client
        
        Args:
            api_key: SiliconFlow API key
            base_url: API base URL
            model: Model name to use
        """
        self.api_key = api_key or Config.SILICONFLOW_API_KEY
        self.base_url = base_url or Config.SILICONFLOW_API_URL
        self.model = model or Config.SILICONFLOW_MODEL
        
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
        
        logger.info(f"SiliconFlow Client initialized with model: {self.model}, base_url: {self.base_url}")
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = None,
                       stream: bool = False,
                       model: Optional[str] = None) -> Dict[str, Any]:
        """
        Send chat completion request to SiliconFlow API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            model: Optional model name to override default
            
        Returns:
            API response dictionary
        """
        try:
            endpoint = f"{self.base_url}/chat/completions"
            
            # 使用指定的模型或默认模型
            selected_model = model or self.model
            
            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            logger.info(f"Sending chat completion request to {endpoint}")
            
            if stream:
                return self._stream_chat_completion(endpoint, payload)
            else:
                response = self.session.post(endpoint, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Chat completion successful, tokens used: {result.get('usage', {})}")
                
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model"),
                    "timestamp": format_timestamp()
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise APIException(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse API response: {e}")
            raise APIException(f"Failed to parse API response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise APIException(f"Unexpected error: {e}")
    
    def _stream_chat_completion(self, endpoint: str, 
                                payload: Dict[str, Any]) -> Generator[str, None, None]:
        """
        Stream chat completion response
        
        Args:
            endpoint: API endpoint
            payload: Request payload
            
        Yields:
            Content chunks
        """
        try:
            response = self.session.post(endpoint, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming request failed: {e}")
            raise APIException(f"Streaming request failed: {e}")
    
    def simple_chat(self, user_message: str, 
                   system_prompt: Optional[str] = None,
                   temperature: float = 0.7,
                   model: Optional[str] = None) -> Dict[str, Any]:
        """
        Simple chat interface with optional system prompt
        
        Args:
            user_message: User's message
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            model: Optional AI model name to use
            
        Returns:
            Response dictionary
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": sanitize_text(user_message)
        })
        
        return self.chat_completion(messages, temperature=temperature, model=model)
    
    def chat_with_knowledge(self, user_message: str,
                           knowledge_context: str,
                           system_prompt: Optional[str] = None,
                           temperature: float = 0.7,
                           model: Optional[str] = None) -> Dict[str, Any]:
        """
        Chat with knowledge base context
        
        Args:
            user_message: User's message
            knowledge_context: Knowledge base context
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            model: Optional AI model name to use
            
        Returns:
            Response dictionary
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        enhanced_message = f"""基于以下知识库信息回答用户的问题：

知识库内容：
{knowledge_context}

用户问题：
{user_message}

请根据知识库内容提供准确、详细的回答。如果知识库中没有相关信息，请诚实说明。"""
        
        messages.append({
            "role": "user",
            "content": sanitize_text(enhanced_message)
        })
        
        return self.chat_completion(messages, temperature=temperature, model=model)
    
    def batch_chat(self, messages_list: List[List[Dict[str, str]]],
                  temperature: float = 0.7) -> List[Dict[str, Any]]:
        """
        Process multiple chat requests in batch
        
        Args:
            messages_list: List of message lists
            temperature: Sampling temperature
            
        Returns:
            List of response dictionaries
        """
        results = []
        
        for i, messages in enumerate(messages_list):
            try:
                result = self.chat_completion(messages, temperature=temperature)
                results.append({
                    "index": i,
                    "success": True,
                    "response": result
                })
            except APIException as e:
                logger.error(f"Batch chat failed for index {i}: {e}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary
        """
        return {
            "model": self.model,
            "api_provider": "SiliconFlow",
            "base_url": self.base_url,
            "timestamp": format_timestamp()
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection
        
        Returns:
            Connection test result
        """
        try:
            test_messages = [
                {"role": "user", "content": "Hello, this is a connection test."}
            ]
            
            result = self.chat_completion(test_messages, max_tokens=10)
            
            return {
                "success": True,
                "message": "Connection successful",
                "model": self.model,
                "timestamp": format_timestamp()
            }
            
        except APIException as e:
            return {
                "success": False,
                "message": f"Connection failed: {e}",
                "timestamp": format_timestamp()
            }
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation)
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text.split()) * 1.3
    
    def validate_message(self, message: Dict[str, str]) -> bool:
        """
        Validate message format
        
        Args:
            message: Message dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_keys = {"role", "content"}
        valid_roles = {"system", "user", "assistant"}
        
        if not all(key in message for key in required_keys):
            return False
        
        if message["role"] not in valid_roles:
            return False
        
        if not message["content"] or not message["content"].strip():
            return False
        
        return True
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format and validate messages
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted messages list
        """
        formatted = []
        
        for msg in messages:
            if self.validate_message(msg):
                formatted.append({
                    "role": msg["role"],
                    "content": sanitize_text(msg["content"])
                })
            else:
                logger.warning(f"Invalid message format, skipping: {msg}")
        
        return formatted
    
    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("SiliconFlow client session closed")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from SiliconFlow API
        
        Returns:
            List of available models with their details
        """
        try:
            endpoint = f"{self.base_url}/models"
            
            logger.info(f"Fetching available models from {endpoint}")
            
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            models = []
            if "data" in result:
                for model in result["data"]:
                    models.append({
                        "id": model.get("id"),
                        "name": model.get("id", "").split("/")[-1] if model.get("id") else "",
                        "object": model.get("object", "model"),
                        "owned_by": model.get("owned_by", ""),
                        "capabilities": model.get("capabilities", {}),
                        "context_length": model.get("context_length", 0)
                    })
            
            logger.info(f"Successfully retrieved {len(models)} available models")
            
            return {
                "success": True,
                "models": models,
                "total": len(models),
                "timestamp": format_timestamp()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch models: {e}")
            raise APIException(f"Failed to fetch models: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching models: {e}")
            raise APIException(f"Unexpected error: {e}")