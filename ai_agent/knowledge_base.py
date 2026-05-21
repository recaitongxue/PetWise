"""
Knowledge Base Management Module
Handles knowledge base import, storage, and retrieval
"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import Config
from utils import (
    ensure_directory, load_json_file, save_json_file, 
    setup_logging, format_timestamp
)
from exceptions import KnowledgeBaseException

logger = setup_logging(Config.LOG_LEVEL)

class KnowledgeBase:
    """Knowledge Base Manager"""
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize Knowledge Base
        
        Args:
            knowledge_base_path: Path to knowledge base file
        """
        self.knowledge_base_path = knowledge_base_path or Config.KNOWLEDGE_BASE_FILE
        self.knowledge_base = self._load_knowledge_base()
        logger.info(f"Knowledge Base initialized with {len(self.knowledge_base)} entries")
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load knowledge base from file"""
        ensure_directory(os.path.dirname(self.knowledge_base_path))
        data = load_json_file(self.knowledge_base_path)
        
        # 如果是结构化的知识库格式（包含categories），转换为内部存储格式
        if "categories" in data:
            return self._convert_structured_to_internal(data)
        
        return data
    
    def _convert_structured_to_internal(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert structured knowledge base format to internal format"""
        internal = {}
        
        if "categories" in structured_data:
            for category_name, category_data in structured_data["categories"].items():
                entries = category_data.get("entries", [])
                for entry in entries:
                    knowledge_id = entry.get("id", f"kb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
                    internal[knowledge_id] = {
                        "id": knowledge_id,
                        "category": category_data.get("name", category_name),
                        "data": entry,
                        "created_at": format_timestamp(),
                        "updated_at": format_timestamp()
                    }
        
        return internal
    
    def _save_knowledge_base(self) -> None:
        """Save knowledge base to file"""
        save_json_file(self.knowledge_base_path, self.knowledge_base)
        logger.info(f"Knowledge base saved to {self.knowledge_base_path}")
    
    def import_knowledge(self, knowledge_data: Dict[str, Any], 
                        category: str = "general") -> Dict[str, Any]:
        """
        Import knowledge into knowledge base
        
        Args:
            knowledge_data: Dictionary containing knowledge data
            category: Category of the knowledge
            
        Returns:
            Import result with status and details
        """
        try:
            knowledge_id = f"kb_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            knowledge_entry = {
                "id": knowledge_id,
                "category": category,
                "data": knowledge_data,
                "created_at": format_timestamp(),
                "updated_at": format_timestamp()
            }
            
            self.knowledge_base[knowledge_id] = knowledge_entry
            self._save_knowledge_base()
            
            logger.info(f"Knowledge imported successfully: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "message": "Knowledge imported successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to import knowledge: {e}")
            raise KnowledgeBaseException(f"Failed to import knowledge: {e}")
    
    def import_from_file(self, file_path: str, 
                        category: str = "general") -> Dict[str, Any]:
        """
        Import knowledge from JSON file
        
        Args:
            file_path: Path to JSON file containing knowledge data
            category: Category of the knowledge
            
        Returns:
            Import result
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
            
            return self.import_knowledge(knowledge_data, category)
            
        except json.JSONDecodeError as e:
            raise KnowledgeBaseException(f"Invalid JSON file: {e}")
        except Exception as e:
            raise KnowledgeBaseException(f"Failed to import from file: {e}")
    
    def query_knowledge(self, query: str, category: Optional[str] = None, 
                       limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query knowledge base
        
        Args:
            query: Search query string
            category: Filter by category (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge entries
        """
        results = []
        query_lower = query.lower()
        
        for kb_id, entry in self.knowledge_base.items():
            if category and entry.get("category") != category:
                continue
            
            data_str = json.dumps(entry.get("data", {}), ensure_ascii=False).lower()
            
            if query_lower in data_str:
                results.append({
                    "id": kb_id,
                    "category": entry.get("category"),
                    "data": entry.get("data"),
                    "relevance": self._calculate_relevance(query_lower, data_str),
                    "created_at": entry.get("created_at")
                })
        
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score for search results"""
        query_words = set(query.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        matches = len(query_words & content_words)
        return matches / len(query_words)
    
    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        Get knowledge entry by ID
        
        Args:
            knowledge_id: Knowledge entry ID
            
        Returns:
            Knowledge entry or None if not found
        """
        return self.knowledge_base.get(knowledge_id)
    
    def get_all_categories(self) -> List[str]:
        """Get all categories in knowledge base"""
        categories = set()
        for entry in self.knowledge_base.values():
            categories.add(entry.get("category", "general"))
        return list(categories)
    
    def update_knowledge(self, knowledge_id: str, 
                        new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing knowledge entry
        
        Args:
            knowledge_id: Knowledge entry ID
            new_data: New data to update
            
        Returns:
            Update result
        """
        if knowledge_id not in self.knowledge_base:
            raise KnowledgeBaseException(f"Knowledge ID not found: {knowledge_id}")
        
        try:
            self.knowledge_base[knowledge_id]["data"] = new_data
            self.knowledge_base[knowledge_id]["updated_at"] = format_timestamp()
            self._save_knowledge_base()
            
            logger.info(f"Knowledge updated successfully: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "message": "Knowledge updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to update knowledge: {e}")
            raise KnowledgeBaseException(f"Failed to update knowledge: {e}")
    
    def delete_knowledge(self, knowledge_id: str) -> Dict[str, Any]:
        """
        Delete knowledge entry
        
        Args:
            knowledge_id: Knowledge entry ID
            
        Returns:
            Delete result
        """
        if knowledge_id not in self.knowledge_base:
            raise KnowledgeBaseException(f"Knowledge ID not found: {knowledge_id}")
        
        try:
            del self.knowledge_base[knowledge_id]
            self._save_knowledge_base()
            
            logger.info(f"Knowledge deleted successfully: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "message": "Knowledge deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {e}")
            raise KnowledgeBaseException(f"Failed to delete knowledge: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        categories = {}
        for entry in self.knowledge_base.values():
            category = entry.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_entries": len(self.knowledge_base),
            "categories": categories,
            "last_updated": format_timestamp()
        }
    
    def export_knowledge(self, output_path: str) -> Dict[str, Any]:
        """
        Export knowledge base to file
        
        Args:
            output_path: Path to export file
            
        Returns:
            Export result
        """
        try:
            ensure_directory(os.path.dirname(output_path))
            save_json_file(output_path, self.knowledge_base)
            
            logger.info(f"Knowledge base exported to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "total_entries": len(self.knowledge_base),
                "message": "Knowledge base exported successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {e}")
            raise KnowledgeBaseException(f"Failed to export knowledge base: {e}")