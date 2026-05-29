"""
System Prompt Management Module
Handles system prompts for AI interactions
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import Config
from utils import (
    ensure_directory, load_text_file, save_text_file, 
    setup_logging, format_timestamp
)
from exceptions import PromptException

logger = setup_logging(Config.LOG_LEVEL)

class PromptManager:
    """System Prompt Manager"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize Prompt Manager
        
        Args:
            prompts_dir: Directory to store prompts
        """
        self.prompts_dir = prompts_dir or Config.PROMPTS_DIR
        ensure_directory(self.prompts_dir)
        self.system_prompt_file = os.path.join(self.prompts_dir, "system_prompt.txt")
        self.custom_prompts_file = os.path.join(self.prompts_dir, "custom_prompts.json")
        
        logger.info(f"Prompt Manager initialized with directory: {self.prompts_dir}")
    
    def get_system_prompt(self) -> str:
        """
        Get the main system prompt
        
        Returns:
            System prompt string
        """
        prompt = load_text_file(self.system_prompt_file)
        
        if not prompt:
            prompt = self._get_default_system_prompt()
            self.save_system_prompt(prompt)
        
        return prompt
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for pet service"""
        return """你是一个专业的宠物智能识别和服务助手，专门为宠物主人提供准确、贴心的服务。

你的主要职责包括：
1. 宠物识别：根据用户提供的图片或描述，准确识别宠物品种、年龄、健康状况等基本信息
2. 健康咨询：提供宠物健康相关的专业建议，包括饮食、运动、疾病预防等
3. 行为分析：分析宠物的行为模式，提供训练和改善建议
4. 应急处理：在宠物遇到紧急情况时，提供初步的应急指导
5. 日常护理：提供宠物日常护理的专业建议，包括美容、清洁等

回答要求：
- 使用专业但易懂的语言，避免过于技术化的术语
- 对于不确定的信息，要诚实说明并建议咨询专业兽医
- 提供实用、可操作的建议
- 保持友好、耐心的态度
- 在涉及健康问题时，始终强调专业诊断的重要性
- 如果用户描述的情况需要紧急医疗处理，要明确提醒并建议立即就医

请根据用户的具体问题，结合你的专业知识，提供最准确和有用的回答。"""
    
    def save_system_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Save system prompt
        
        Args:
            prompt: System prompt content
            
        Returns:
            Save result
        """
        try:
            save_text_file(self.system_prompt_file, prompt)
            logger.info("System prompt saved successfully")
            
            return {
                "success": True,
                "message": "System prompt saved successfully",
                "timestamp": format_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Failed to save system prompt: {e}")
            raise PromptException(f"Failed to save system prompt: {e}")
    
    def update_system_prompt(self, new_content: str) -> Dict[str, Any]:
        """
        Update system prompt
        
        Args:
            new_content: New system prompt content
            
        Returns:
            Update result
        """
        return self.save_system_prompt(new_content)
    
    def create_custom_prompt(self, name: str, content: str, 
                            description: str = "") -> Dict[str, Any]:
        """
        Create a custom prompt
        
        Args:
            name: Prompt name
            content: Prompt content
            description: Prompt description
            
        Returns:
            Creation result
        """
        try:
            custom_prompts = self._load_custom_prompts()
            
            if name in custom_prompts:
                raise PromptException(f"Prompt '{name}' already exists")
            
            prompt_entry = {
                "name": name,
                "content": content,
                "description": description,
                "created_at": format_timestamp(),
                "updated_at": format_timestamp()
            }
            
            custom_prompts[name] = prompt_entry
            self._save_custom_prompts(custom_prompts)
            
            logger.info(f"Custom prompt created: {name}")
            return {
                "success": True,
                "prompt_name": name,
                "message": "Custom prompt created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create custom prompt: {e}")
            raise PromptException(f"Failed to create custom prompt: {e}")
    
    def _load_custom_prompts(self) -> Dict[str, Any]:
        """Load custom prompts from file"""
        import json
        try:
            with open(self.custom_prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
    def _save_custom_prompts(self, prompts: Dict[str, Any]) -> None:
        """Save custom prompts to file"""
        import json
        with open(self.custom_prompts_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
    
    def get_custom_prompt(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get custom prompt by name
        
        Args:
            name: Prompt name
            
        Returns:
            Prompt entry or None if not found
        """
        custom_prompts = self._load_custom_prompts()
        return custom_prompts.get(name)
    
    def list_custom_prompts(self) -> List[Dict[str, Any]]:
        """
        List all custom prompts
        
        Returns:
            List of custom prompts
        """
        custom_prompts = self._load_custom_prompts()
        return [
            {
                "name": name,
                "description": prompt.get("description", ""),
                "created_at": prompt.get("created_at"),
                "updated_at": prompt.get("updated_at")
            }
            for name, prompt in custom_prompts.items()
        ]
    
    def update_custom_prompt(self, name: str, content: Optional[str] = None,
                            description: Optional[str] = None) -> Dict[str, Any]:
        """
        Update custom prompt
        
        Args:
            name: Prompt name
            content: New content (optional)
            description: New description (optional)
            
        Returns:
            Update result
        """
        try:
            custom_prompts = self._load_custom_prompts()
            
            if name not in custom_prompts:
                raise PromptException(f"Prompt '{name}' not found")
            
            if content is not None:
                custom_prompts[name]["content"] = content
            if description is not None:
                custom_prompts[name]["description"] = description
            
            custom_prompts[name]["updated_at"] = format_timestamp()
            self._save_custom_prompts(custom_prompts)
            
            logger.info(f"Custom prompt updated: {name}")
            return {
                "success": True,
                "prompt_name": name,
                "message": "Custom prompt updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update custom prompt: {e}")
            raise PromptException(f"Failed to update custom prompt: {e}")
    
    def delete_custom_prompt(self, name: str) -> Dict[str, Any]:
        """
        Delete custom prompt
        
        Args:
            name: Prompt name
            
        Returns:
            Delete result
        """
        try:
            custom_prompts = self._load_custom_prompts()
            
            if name not in custom_prompts:
                raise PromptException(f"Prompt '{name}' not found")
            
            del custom_prompts[name]
            self._save_custom_prompts(custom_prompts)
            
            logger.info(f"Custom prompt deleted: {name}")
            return {
                "success": True,
                "prompt_name": name,
                "message": "Custom prompt deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete custom prompt: {e}")
            raise PromptException(f"Failed to delete custom prompt: {e}")
    
    def get_combined_prompt(self, custom_prompt_name: Optional[str] = None) -> str:
        """
        Get combined system prompt with optional custom prompt
        
        Args:
            custom_prompt_name: Name of custom prompt to include (optional)
            
        Returns:
            Combined prompt string
        """
        system_prompt = self.get_system_prompt()
        
        if custom_prompt_name:
            custom_prompt = self.get_custom_prompt(custom_prompt_name)
            if custom_prompt:
                system_prompt += f"\n\n{custom_prompt['content']}"
        
        return system_prompt
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Validate prompt content
        
        Args:
            prompt: Prompt content to validate
            
        Returns:
            Validation result
        """
        issues = []
        
        if not prompt or not prompt.strip():
            issues.append("Prompt cannot be empty")
        
        if len(prompt) < 50:
            issues.append("Prompt is too short (minimum 50 characters)")
        
        if len(prompt) > 10000:
            issues.append("Prompt is too long (maximum 10000 characters)")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "length": len(prompt)
        }