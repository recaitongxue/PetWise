"""
Knowledge Base Management Module
Handles knowledge base import, storage, and retrieval using SQLite
"""
import json
import os
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

from config import Config
from utils import (
    ensure_directory, load_json_file, 
    setup_logging, format_timestamp
)
from exceptions import KnowledgeBaseException

logger = setup_logging(Config.LOG_LEVEL)

class KnowledgeBase:
    """Knowledge Base Manager using SQLite"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Knowledge Base
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or Config.KNOWLEDGE_DB_PATH
        ensure_directory(os.path.dirname(self.db_path))
        self._init_database()
        self._migrate_from_json()
        logger.info(f"Knowledge Base initialized with SQLite: {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database and create tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT,
                    data TEXT NOT NULL,
                    keywords TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_knowledge_keywords ON knowledge(keywords)
            ''')
            
            conn.commit()
    
    def _migrate_from_json(self):
        """Migrate data from JSON file to SQLite if DB is empty"""
        json_path = Config.KNOWLEDGE_BASE_FILE
        
        if not os.path.exists(json_path):
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            count = cursor.fetchone()[0]
            
            if count > 0:
                return
        
        logger.info("Migrating knowledge from JSON to SQLite...")
        
        try:
            data = load_json_file(json_path)
            
            if "categories" in data:
                self._import_structured_data(data)
            else:
                self._import_legacy_data(data)
            
            logger.info("Migration completed successfully")
        except Exception as e:
            logger.warning(f"Failed to migrate from JSON: {e}")
    
    def _import_structured_data(self, structured_data: Dict[str, Any]):
        """Import structured knowledge base format"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for category_name, category_data in structured_data["categories"].items():
                category_display_name = category_data.get("name", category_name)
                category_description = category_data.get("description", "")
                
                cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                    (category_display_name, category_description, format_timestamp()))
                
                entries = category_data.get("entries", [])
                for entry in entries:
                    knowledge_id = entry.get("id", f"kb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
                    title = entry.get("title", entry.get("name", ""))
                    data_json = json.dumps(entry, ensure_ascii=False)
                    keywords = self._extract_keywords(entry)
                    
                    cursor.execute('INSERT OR IGNORE INTO knowledge (id, category, title, data, keywords, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (knowledge_id, category_display_name, title, data_json, keywords, format_timestamp(), format_timestamp()))
            
            conn.commit()
    
    def _import_legacy_data(self, legacy_data: Dict[str, Any]):
        """Import legacy knowledge base format"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for kb_id, entry in legacy_data.items():
                category = entry.get("category", "general")
                title = entry.get("title", "")
                data = entry.get("data", {})
                data_json = json.dumps(data, ensure_ascii=False)
                keywords = self._extract_keywords(data)
                created_at = entry.get("created_at", format_timestamp())
                updated_at = entry.get("updated_at", format_timestamp())
                
                cursor.execute('INSERT OR IGNORE INTO knowledge (id, category, title, data, keywords, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (kb_id, category, title, data_json, keywords, created_at, updated_at))
            
            conn.commit()
    
    def _extract_keywords(self, data: Dict[str, Any]) -> str:
        """Extract keywords from knowledge entry for search"""
        keywords = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    keywords.append(value)
                elif isinstance(value, (list, dict)):
                    keywords.extend(self._extract_keywords(value))
        
        return ",".join(keywords[:50])
    
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
            title = knowledge_data.get("title", knowledge_data.get("name", ""))
            data_json = json.dumps(knowledge_data, ensure_ascii=False)
            keywords = self._extract_keywords(knowledge_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                    (category, "", format_timestamp()))
                
                cursor.execute('INSERT INTO knowledge (id, category, title, data, keywords, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (knowledge_id, category, title, data_json, keywords, format_timestamp(), format_timestamp()))
                
                conn.commit()
            
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
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('SELECT * FROM knowledge WHERE category = ? ORDER BY updated_at DESC LIMIT ?',
                        (category, limit))
                else:
                    cursor.execute('SELECT * FROM knowledge ORDER BY updated_at DESC LIMIT ?', (limit,))
                
                for row in cursor.fetchall():
                    data = json.loads(row['data'])
                    data_str = json.dumps(data, ensure_ascii=False).lower()
                    
                    if query_lower in data_str or query_lower in row['keywords'].lower():
                        results.append({
                            "id": row['id'],
                            "category": row['category'],
                            "title": row['title'],
                            "data": data,
                            "relevance": self._calculate_relevance(query_lower, data_str),
                            "created_at": row['created_at']
                        })
            
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM knowledge WHERE id = ?', (knowledge_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row['id'],
                        "category": row['category'],
                        "title": row['title'],
                        "data": json.loads(row['data']),
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to get knowledge by ID: {e}")
            return None
    
    def get_all_categories(self) -> List[str]:
        """Get all categories in knowledge base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT name FROM categories ORDER BY name')
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
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
        try:
            data_json = json.dumps(new_data, ensure_ascii=False)
            keywords = self._extract_keywords(new_data)
            title = new_data.get("title", new_data.get("name", ""))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('UPDATE knowledge SET data = ?, title = ?, keywords = ?, updated_at = ? WHERE id = ?',
                    (data_json, title, keywords, format_timestamp(), knowledge_id))
                
                if cursor.rowcount == 0:
                    raise KnowledgeBaseException(f"Knowledge ID not found: {knowledge_id}")
                
                conn.commit()
            
            logger.info(f"Knowledge updated successfully: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "message": "Knowledge updated successfully"
            }
            
        except KnowledgeBaseException:
            raise
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
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM knowledge WHERE id = ?', (knowledge_id,))
                
                if cursor.rowcount == 0:
                    raise KnowledgeBaseException(f"Knowledge ID not found: {knowledge_id}")
                
                conn.commit()
            
            logger.info(f"Knowledge deleted successfully: {knowledge_id}")
            return {
                "success": True,
                "knowledge_id": knowledge_id,
                "message": "Knowledge deleted successfully"
            }
            
        except KnowledgeBaseException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete knowledge: {e}")
            raise KnowledgeBaseException(f"Failed to delete knowledge: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM knowledge')
                total_entries = cursor.fetchone()[0]
                
                cursor.execute('SELECT category, COUNT(*) FROM knowledge GROUP BY category')
                categories = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('SELECT COUNT(*) FROM categories')
                category_count = cursor.fetchone()[0]
                
                return {
                    "total_entries": total_entries,
                    "categories": categories,
                    "category_count": category_count,
                    "last_updated": format_timestamp()
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "total_entries": 0,
                "categories": {},
                "category_count": 0,
                "last_updated": format_timestamp()
            }
    
    def export_knowledge(self, output_path: str) -> Dict[str, Any]:
        """
        Export knowledge base to JSON file
        
        Args:
            output_path: Path to export file
            
        Returns:
            Export result
        """
        try:
            ensure_directory(os.path.dirname(output_path))
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM knowledge ORDER BY category, created_at')
                knowledge_data = {}
                
                for row in cursor.fetchall():
                    knowledge_data[row['id']] = {
                        "id": row['id'],
                        "category": row['category'],
                        "title": row['title'],
                        "data": json.loads(row['data']),
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Knowledge base exported to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "total_entries": len(knowledge_data),
                "message": "Knowledge base exported successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {e}")
            raise KnowledgeBaseException(f"Failed to export knowledge base: {e}")
    
    def add_category(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Add a new category
        
        Args:
            name: Category name
            description: Category description
            
        Returns:
            Result dictionary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                    (name, description, format_timestamp()))
                
                if cursor.rowcount == 0:
                    return {
                        "success": False,
                        "message": "Category already exists"
                    }
                
                conn.commit()
            
            logger.info(f"Category added: {name}")
            return {
                "success": True,
                "name": name,
                "message": "Category added successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to add category: {e}")
            raise KnowledgeBaseException(f"Failed to add category: {e}")
    
    def get_category_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get category information
        
        Args:
            name: Category name
            
        Returns:
            Category info or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM categories WHERE name = ?', (name,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "name": row['name'],
                        "description": row['description'],
                        "created_at": row['created_at']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to get category info: {e}")
            return None