"""
AI Agent Configuration Module
Manages environment variables and configuration settings
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for AI Agent"""
    
    # SiliconFlow API Configuration
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    SILICONFLOW_API_URL: str = os.getenv("SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1")
    SILICONFLOW_MODEL: str = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_DIR: str = os.path.join(os.path.dirname(__file__), "knowledge_base")
    KNOWLEDGE_BASE_FILE: str = os.path.join(KNOWLEDGE_BASE_DIR, "pet_knowledge.json")
    
    # System Prompts Configuration
    PROMPTS_DIR: str = os.path.join(os.path.dirname(__file__), "prompts")
    SYSTEM_PROMPT_FILE: str = os.path.join(PROMPTS_DIR, "system_prompt.txt")
    
    # API Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.SILICONFLOW_API_KEY:
            raise ValueError("SILICONFLOW_API_KEY is required")
        return True

    @classmethod
    def get_api_config(cls) -> dict:
        """Get API configuration for SiliconFlow"""
        return {
            "api_key": cls.SILICONFLOW_API_KEY,
            "base_url": cls.SILICONFLOW_API_URL,
            "model": cls.SILICONFLOW_MODEL
        }