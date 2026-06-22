"""
Unit tests for configuration module
"""
import pytest
import os
from config import Config


class TestConfig:
    """Tests for Config class"""

    def test_config_defaults(self):
        """Test default configuration values"""
        assert Config.API_HOST == "0.0.0.0"
        assert Config.API_PORT == 8000
        assert Config.SILICONFLOW_MODEL == "deepseek-ai/DeepSeek-V3"
        assert Config.CACHE_ENABLED is True
        assert Config.CACHE_TTL == 300
        assert Config.CACHE_MAX_SIZE == 100

    def test_config_env_file_exists(self):
        """Test that .env file exists"""
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        assert os.path.exists(env_path), ".env file should exist"

    def test_config_validate(self):
        """Test configuration validation"""
        # Should raise ValueError if API key is missing
        original_key = Config.SILICONFLOW_API_KEY
        Config.SILICONFLOW_API_KEY = ""
        
        with pytest.raises(ValueError, match="SILICONFLOW_API_KEY is required"):
            Config.validate()
        
        # Restore original value
        Config.SILICONFLOW_API_KEY = original_key

    def test_get_cors_origins(self):
        """Test CORS origins parsing"""
        origins = Config.get_cors_origins()
        assert isinstance(origins, list)
        assert len(origins) >= 1