"""
AI Agent Configuration Module
Manages environment variables and configuration settings
"""
import os
from typing import Optional, List
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
    KNOWLEDGE_DB_PATH: str = os.path.join(KNOWLEDGE_BASE_DIR, "knowledge.db")
    
    # System Prompts Configuration
    PROMPTS_DIR: str = os.path.join(os.path.dirname(__file__), "prompts")
    SYSTEM_PROMPT_FILE: str = os.path.join(PROMPTS_DIR, "system_prompt.txt")
    
    # API Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    # Cache Configuration
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "100"))
    
    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "structured")
    
    # Models Configuration
    MODELS_CACHE_TTL: int = int(os.getenv("MODELS_CACHE_TTL", "3600"))
    
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
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS allowed origins"""
        return [origin.strip() for origin in cls.CORS_ORIGINS if origin.strip()]