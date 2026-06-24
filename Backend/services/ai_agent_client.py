"""
AI Agent Client Module
Provides interface to call ai_agent services from backend
"""
import requests
import json
from typing import Dict, Any, Optional, Generator

class AIAgentClient:
    """Client for interacting with AI Agent Service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.default_model_config = None
        self.default_embedding_config = None
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to AI Agent service"""
        try:
            url = f"{self.base_url}{endpoint}"
            kwargs.setdefault('timeout', 30)
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def set_default_model_config(self, config: Dict[str, Any]):
        """Set the default model configuration from database"""
        self.default_model_config = config
    
    def set_default_embedding_config(self, config: Dict[str, Any]):
        """Set the default embedding model configuration from database"""
        self.default_embedding_config = config
        self._update_ai_agent_embedding_config(config)
    
    def _get_chat_data(self, user_message: str, use_knowledge_base: bool, custom_prompt: Optional[str],
                       temperature: float, model: Optional[str], pet_context: Optional[Dict[str, Any]],
                       breed_context: Optional[str]) -> Dict[str, Any]:
        """Build chat request data with model configuration"""
        data = {
            "user_message": user_message,
            "use_knowledge_base": use_knowledge_base,
            "temperature": temperature
        }
        
        if self.default_model_config:
            if "api_key" in self.default_model_config and self.default_model_config["api_key"]:
                data["api_key"] = self.default_model_config["api_key"]
            if "base_url" in self.default_model_config and self.default_model_config["base_url"]:
                base_url = self.default_model_config["base_url"]
                if not base_url.endswith('/v1'):
                    base_url = base_url.rstrip('/') + '/v1'
                data["base_url"] = base_url
        
        if custom_prompt:
            data["custom_prompt"] = custom_prompt
        if model:
            data["model"] = model
        elif self.default_model_config and "model_name" in self.default_model_config:
            data["model"] = self.default_model_config["model_name"]
        if pet_context:
            data["pet_context"] = pet_context
        if breed_context:
            data["breed_context"] = breed_context
        
        return data
    
    def stream_chat(self, user_message: str,
                    use_knowledge_base: bool = True,
                    custom_prompt: Optional[str] = None,
                    temperature: float = 0.7,
                    model: Optional[str] = None,
                    pet_context: Optional[Dict[str, Any]] = None,
                    breed_context: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat with AI agent (returns generator)"""
        url = f"{self.base_url}/v1/stream"
        data = self._get_chat_data(user_message, use_knowledge_base, custom_prompt,
                                   temperature, model, pet_context, breed_context)
        
        try:
            response = requests.post(url, json=data, stream=True)
            response.raise_for_status()
            
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                buffer += chunk
                while "\n\n" in buffer:
                    line, buffer = buffer.split("\n\n", 1)
                    if line.startswith("data: "):
                        yield line[6:]
        except requests.exceptions.RequestException as e:
            yield f'Error: {str(e)}'
    
    def chat(self, user_message: str, 
             use_knowledge_base: bool = True,
             custom_prompt: Optional[str] = None,
             temperature: float = 0.7,
             model: Optional[str] = None,
             pet_context: Optional[Dict[str, Any]] = None,
             breed_context: Optional[str] = None) -> Dict[str, Any]:
        """Chat with AI agent"""
        data = self._get_chat_data(user_message, use_knowledge_base, custom_prompt,
                                   temperature, model, pet_context, breed_context)
        
        return self._request("POST", "/v1/chat", json=data)
    
    def get_pet_advice(self, topic: str, pet_type: Optional[str] = None, 
                       specific_issue: Optional[str] = None) -> Dict[str, Any]:
        """Get pet care advice"""
        data = {"topic": topic}
        if pet_type:
            data["pet_type"] = pet_type
        if specific_issue:
            data["specific_issue"] = specific_issue
        
        return self._request("POST", "/v1/advice", json=data)
    
    def emergency_consultation(self, symptoms: str, pet_type: str, 
                               severity: str = "medium") -> Dict[str, Any]:
        """Emergency consultation"""
        data = {
            "symptoms": symptoms,
            "pet_type": pet_type,
            "severity": severity
        }
        return self._request("POST", "/v1/emergency", json=data)

    def structured_consultation(self, pet_id: int,
                               symptoms: list,
                               duration: Optional[str] = None,
                               severity: str = "medium",
                               additional_info: Optional[str] = None,
                               pet_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Structured consultation"""
        data = {
            "pet_id": pet_id,
            "symptoms": symptoms,
            "severity": severity
        }
        if duration:
            data["duration"] = duration
        if additional_info:
            data["additional_info"] = additional_info
        if pet_context:
            data["pet_context"] = pet_context
        return self._request("POST", "/v1/structured-consultation", json=data)
    
    def analyze_image(self, image_data: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze pet image"""
        data = {
            "image_data": image_data,
            "analysis_type": analysis_type
        }
        return self._request("POST", "/v1/analyze-image", json=data)
    
    def health_check(self) -> Dict[str, Any]:
        """Check AI Agent service health"""
        return self._request("GET", "/health")
    
    def get_info(self) -> Dict[str, Any]:
        """Get service information"""
        return self._request("GET", "/info")
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models"""
        return self._request("GET", "/v1/models")
    
    def knowledge_query(self, query: str, category: Optional[str] = None, 
                        limit: int = 5) -> Dict[str, Any]:
        """Query knowledge base"""
        data = {"query": query, "limit": limit}
        if category:
            data["category"] = category
        return self._request("POST", "/v1/knowledge/query", json=data)
    
    def knowledge_query_all(self, category: Optional[str] = None,
                            page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get all knowledge entries with pagination"""
        params = {"page": page, "per_page": per_page}
        if category:
            params["category"] = category
        return self._request("GET", "/v1/knowledge/list", params=params)
    
    def knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return self._request("GET", "/v1/knowledge/stats")
    
    def knowledge_import(self, knowledge_data: Dict[str, Any], 
                         category: str = "general") -> Dict[str, Any]:
        """Import knowledge"""
        data = {
            "knowledge_data": knowledge_data,
            "category": category
        }
        return self._request("POST", "/v1/knowledge/import", json=data)
    
    def get_knowledge_categories(self) -> Dict[str, Any]:
        """Get knowledge categories"""
        return self._request("GET", "/v1/knowledge/categories")
    
    def upload_knowledge_file(self, file, category: str = "general") -> Dict[str, Any]:
        """
        Upload knowledge file to AI Agent service
        
        Args:
            file: File object from Flask request
            category: Knowledge category
            
        Returns:
            Upload result
        """
        try:
            url = f"{self.base_url}/v1/knowledge/upload"
            
            files = {
                'file': (file.filename, file.stream, file.content_type)
            }
            
            data = {
                'category': category
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def _update_ai_agent_embedding_config(self, config: Dict[str, Any]):
        """Update AI Agent service with embedding model configuration"""
        try:
            url = f"{self.base_url}/v1/embedding/config"
            data = {
                "api_key": config.get("api_key"),
                "base_url": config.get("base_url"),
                "model_name": config.get("model_name"),
                "embedding_dim": config.get("embedding_dim", 0)
            }
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to update AI Agent embedding config: {e}")
            return {"success": False, "error": str(e)}


# Global client instance
ai_client = AIAgentClient()