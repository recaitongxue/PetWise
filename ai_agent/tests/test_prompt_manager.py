"""
Unit tests for prompt manager module
"""
import pytest
import tempfile
import os
import shutil
from prompt_manager import PromptManager


class TestPromptManager:
    """Tests for PromptManager class"""

    @pytest.fixture
    def temp_prompt_manager(self):
        """Create a temporary prompt manager for testing"""
        temp_dir = tempfile.mkdtemp()
        pm = PromptManager(prompts_dir=temp_dir)
        yield pm
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_get_system_prompt(self, temp_prompt_manager):
        """Test getting system prompt"""
        prompt = temp_prompt_manager.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_create_custom_prompt(self, temp_prompt_manager):
        """Test creating custom prompt"""
        result = temp_prompt_manager.create_custom_prompt(
            name="test_prompt",
            content="This is a test prompt",
            description="Test description"
        )
        
        assert result["success"] is True
        assert result["prompt_name"] == "test_prompt"

    def test_create_duplicate_prompt(self, temp_prompt_manager):
        """Test creating duplicate prompt"""
        temp_prompt_manager.create_custom_prompt(
            name="duplicate",
            content="Content"
        )
        
        with pytest.raises(Exception, match="already exists"):
            temp_prompt_manager.create_custom_prompt(
                name="duplicate",
                content="Different content"
            )

    def test_get_custom_prompt(self, temp_prompt_manager):
        """Test getting custom prompt"""
        temp_prompt_manager.create_custom_prompt(
            name="my_prompt",
            content="My content",
            description="My description"
        )
        
        prompt = temp_prompt_manager.get_custom_prompt("my_prompt")
        assert prompt is not None
        assert prompt["name"] == "my_prompt"
        assert prompt["content"] == "My content"

    def test_get_nonexistent_prompt(self, temp_prompt_manager):
        """Test getting nonexistent prompt"""
        prompt = temp_prompt_manager.get_custom_prompt("nonexistent")
        assert prompt is None

    def test_list_custom_prompts(self, temp_prompt_manager):
        """Test listing custom prompts"""
        temp_prompt_manager.create_custom_prompt(
            name="prompt1",
            content="Content 1"
        )
        temp_prompt_manager.create_custom_prompt(
            name="prompt2",
            content="Content 2"
        )
        
        prompts = temp_prompt_manager.list_custom_prompts()
        assert len(prompts) == 2
        prompt_names = [p["name"] for p in prompts]
        assert "prompt1" in prompt_names
        assert "prompt2" in prompt_names

    def test_update_custom_prompt(self, temp_prompt_manager):
        """Test updating custom prompt"""
        temp_prompt_manager.create_custom_prompt(
            name="to_update",
            content="Original",
            description="Original desc"
        )
        
        result = temp_prompt_manager.update_custom_prompt(
            name="to_update",
            content="Updated",
            description="Updated desc"
        )
        
        assert result["success"] is True
        
        prompt = temp_prompt_manager.get_custom_prompt("to_update")
        assert prompt["content"] == "Updated"
        assert prompt["description"] == "Updated desc"

    def test_delete_custom_prompt(self, temp_prompt_manager):
        """Test deleting custom prompt"""
        temp_prompt_manager.create_custom_prompt(
            name="to_delete",
            content="Delete me"
        )
        
        assert temp_prompt_manager.get_custom_prompt("to_delete") is not None
        
        result = temp_prompt_manager.delete_custom_prompt("to_delete")
        assert result["success"] is True
        
        assert temp_prompt_manager.get_custom_prompt("to_delete") is None

    def test_prompt_validation(self, temp_prompt_manager):
        """Test prompt validation"""
        # Empty prompt
        result = temp_prompt_manager.validate_prompt("")
        assert result["valid"] is False
        
        # Too short
        result = temp_prompt_manager.validate_prompt("Too short")
        assert result["valid"] is False
        
        # Valid prompt (minimum 50 characters)
        result = temp_prompt_manager.validate_prompt("This is a valid prompt that has sufficient length to pass the validation check.")
        assert result["valid"] is True