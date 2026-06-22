"""
Utility Functions for AI Agent Module
"""
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import os

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("ai_agent")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def ensure_directory(directory_path: str) -> None:
    """Ensure directory exists, create if not"""
    os.makedirs(directory_path, exist_ok=True)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {e}")

def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Save data to JSON file"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_text_file(file_path: str) -> str:
    """Load text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def save_text_file(file_path: str, content: str) -> None:
    """Save content to text file"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def format_timestamp() -> str:
    """Get formatted timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return bool(api_key and len(api_key) > 10)

def sanitize_text(text: str) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    return text.strip()

def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result