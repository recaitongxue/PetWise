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
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to AI Agent service"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def stream_chat(self, user_message: str,
                    use_knowledge_base: bool = True,
                    custom_prompt: Optional[str] = None,
                    temperature: float = 0.7,
                    model: Optional[str] = None,
                    pet_context: Optional[Dict[str, Any]] = None,
                    breed_context: Optional[str] = None) -> Generator[str, None, None]:
        """Stream chat with AI agent (returns generator)"""
        url = f"{self.base_url}/v1/stream"
        data = {
            "user_message": user_message,
            "use_knowledge_base": use_knowledge_base,
            "temperature": temperature
        }
        if custom_prompt:
            data["custom_prompt"] = custom_prompt
        if model:
            data["model"] = model
        if pet_context:
            data["pet_context"] = pet_context
        if breed_context:
            data["breed_context"] = breed_context
        
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
        data = {
            "user_message": user_message,
            "use_knowledge_base": use_knowledge_base,
            "temperature": temperature
        }
        if custom_prompt:
            data["custom_prompt"] = custom_prompt
        if model:
            data["model"] = model
        if pet_context:
            data["pet_context"] = pet_context
        if breed_context:
            data["breed_context"] = breed_context
        
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