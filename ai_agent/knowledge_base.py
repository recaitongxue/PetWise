"""
Knowledge Base Management Module
Handles knowledge base import, storage, and retrieval using SQLite
Enhanced with vector embedding search algorithm
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

try:
    from file_parser import FileParser
    FILE_PARSER_AVAILABLE = True
except ImportError:
    FILE_PARSER_AVAILABLE = False
    logger = setup_logging(Config.LOG_LEVEL)
    logger.warning("File parser module not available, file import will be limited")

try:
    from embedding_client import EmbeddingClient
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logger = setup_logging(Config.LOG_LEVEL)
    logger.warning("Embedding module not available. Using TF-IDF fallback.")

logger = setup_logging(Config.LOG_LEVEL)

try:
    import jieba
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TF_IDF_AVAILABLE = True
except ImportError:
    TF_IDF_AVAILABLE = False
    logger.warning("TF-IDF dependencies not installed. Using basic search.")

class KnowledgeBase:
    """Knowledge Base Manager using SQLite with vector embedding search"""
    
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
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None
        self._document_ids = []
        self._embedding_client = None
        self._embedding_dim = 0
        
        if EMBEDDING_AVAILABLE:
            self.configure_embedding(
                api_key=None,
                base_url="http://localhost:11434",
                model="qwen3-embedding:0.6b",
                embedding_dim=0
            )
        
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
                    full_text TEXT,
                    embedding TEXT,
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
            
            try:
                conn.execute('ALTER TABLE knowledge ADD COLUMN embedding TEXT')
            except sqlite3.OperationalError:
                pass
            
            conn.commit()
    
    def configure_embedding(self, api_key: Optional[str] = None, 
                           base_url: Optional[str] = None,
                           model: Optional[str] = None,
                           embedding_dim: int = 0):
        """
        Configure the embedding client for vector search
        
        Args:
            api_key: API key for embedding service
            base_url: Base URL for embedding service
            model: Embedding model name
            embedding_dim: Expected embedding dimension
        """
        if not EMBEDDING_AVAILABLE:
            logger.warning("Embedding module not available, cannot configure")
            return
        
        if self._embedding_client:
            self._embedding_client.configure(api_key, base_url, model, embedding_dim)
        else:
            self._embedding_client = EmbeddingClient(api_key, base_url, model, embedding_dim)
        
        if embedding_dim > 0:
            self._embedding_dim = embedding_dim
        
        logger.info(f"Embedding configured: model={model}, base_url={base_url}")
    
    def _create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Create embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not EMBEDDING_AVAILABLE or not self._embedding_client:
            return None
        
        try:
            embedding = self._embedding_client.get_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            return None
    
    def _calculate_vector_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            arr1 = np.array(vec1).reshape(1, -1)
            arr2 = np.array(vec2).reshape(1, -1)
            return float(cosine_similarity(arr1, arr2)[0][0])
        except ImportError:
            return self._simple_cosine_similarity(vec1, vec2)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def _simple_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Simple cosine similarity calculation (fallback)
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        if not vec1 or not vec2:
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = (sum(a * a for a in vec1)) ** 0.5
        magnitude2 = (sum(b * b for b in vec2)) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)

    def _migrate_from_json(self):
        """Migrate data from JSON file to SQLite if DB is empty with transaction support"""
        json_path = Config.KNOWLEDGE_BASE_FILE
        
        if not os.path.exists(json_path):
            logger.debug(f"JSON file not found: {json_path}")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            count = cursor.fetchone()[0]
            
            if count > 0:
                logger.debug("Database already has data, skipping migration")
                return
        
        is_temp_db = "temp" in self.db_path.lower() or "tmp" in self.db_path.lower()
        if is_temp_db:
            logger.debug("Skipping migration for temporary database")
            return
        
        logger.info("Starting knowledge migration from JSON to SQLite...")
        
        try:
            data = load_json_file(json_path)
            
            if "categories" in data:
                result = self._import_structured_data(data)
            else:
                result = self._import_legacy_data(data)
            
            if result.get("success", True):
                logger.info("Migration completed successfully")
            else:
                logger.warning(f"Partial migration completed: {result.get('message', '')}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file: {e}")
        except Exception as e:
            logger.error(f"Migration failed with error: {e}", exc_info=True)
    
    def _import_structured_data(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import structured knowledge base format with transaction support"""
        imported_count = 0
        skipped_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    for category_name, category_data in structured_data["categories"].items():
                        category_display_name = category_data.get("name", category_name)
                        category_description = category_data.get("description", "")
                        
                        cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                            (category_display_name, category_description, format_timestamp()))
                        
                        entries = category_data.get("entries", [])
                        for entry in entries:
                            try:
                                knowledge_id = entry.get("id", f"kb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
                                title = entry.get("title", entry.get("name", ""))
                                data_json = json.dumps(entry, ensure_ascii=False)
                                keywords = self._extract_keywords(entry)
                                full_text = self._generate_full_text(entry)
                                
                                cursor.execute('INSERT OR IGNORE INTO knowledge (id, category, title, data, keywords, full_text, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                    (knowledge_id, category_display_name, title, data_json, keywords, full_text, format_timestamp(), format_timestamp()))
                                
                                if cursor.rowcount > 0:
                                    imported_count += 1
                                else:
                                    skipped_count += 1
                            
                            except Exception as e:
                                logger.warning(f"Skipping entry due to error: {e}")
                                skipped_count += 1
                                continue
                    
                    conn.commit()
                    logger.info(f"Structured data import completed: {imported_count} imported, {skipped_count} skipped")
                    
                    return {
                        "success": True,
                        "imported": imported_count,
                        "skipped": skipped_count,
                        "message": f"Successfully imported {imported_count} entries"
                    }
                
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to import structured data, rolled back: {e}")
                    return {
                        "success": False,
                        "imported": imported_count,
                        "skipped": skipped_count,
                        "message": f"Migration failed: {str(e)}"
                    }
                    
        except Exception as e:
            logger.error(f"Database connection error during structured import: {e}")
            return {
                "success": False,
                "imported": 0,
                "skipped": 0,
                "message": f"Database error: {str(e)}"
            }
    
    def _import_legacy_data(self, legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import legacy knowledge base format with transaction support"""
        imported_count = 0
        skipped_count = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    for kb_id, entry in legacy_data.items():
                        try:
                            category = entry.get("category", "general")
                            title = entry.get("title", "")
                            data = entry.get("data", {})
                            data_json = json.dumps(data, ensure_ascii=False)
                            keywords = self._extract_keywords(data)
                            full_text = self._generate_full_text(data)
                            created_at = entry.get("created_at", format_timestamp())
                            updated_at = entry.get("updated_at", format_timestamp())
                            
                            cursor.execute('INSERT OR IGNORE INTO knowledge (id, category, title, data, keywords, full_text, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (kb_id, category, title, data_json, keywords, full_text, created_at, updated_at))
                            
                            if cursor.rowcount > 0:
                                imported_count += 1
                            else:
                                skipped_count += 1
                        
                        except Exception as e:
                            logger.warning(f"Skipping entry {kb_id} due to error: {e}")
                            skipped_count += 1
                            continue
                    
                    conn.commit()
                    logger.info(f"Legacy data import completed: {imported_count} imported, {skipped_count} skipped")
                    
                    return {
                        "success": True,
                        "imported": imported_count,
                        "skipped": skipped_count,
                        "message": f"Successfully imported {imported_count} entries"
                    }
                
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to import legacy data, rolled back: {e}")
                    return {
                        "success": False,
                        "imported": imported_count,
                        "skipped": skipped_count,
                        "message": f"Migration failed: {str(e)}"
                    }
                    
        except Exception as e:
            logger.error(f"Database connection error during legacy import: {e}")
            return {
                "success": False,
                "imported": 0,
                "skipped": 0,
                "message": f"Database error: {str(e)}"
            }
    
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
    
    def _generate_full_text(self, data: Dict[str, Any]) -> str:
        """Generate full text content for TF-IDF indexing"""
        texts = []
        
        def extract_text(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for value in obj.values():
                    extract_text(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text(item)
        
        extract_text(data)
        return " ".join(texts)
    
    def _ensure_tfidf_index(self):
        """Build or refresh TF-IDF index"""
        if not TF_IDF_AVAILABLE:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT id, full_text FROM knowledge')
                rows = cursor.fetchall()
                
                if not rows:
                    self._tfidf_vectorizer = None
                    self._tfidf_matrix = None
                    self._document_ids = []
                    return
                
                documents = [row['full_text'] for row in rows]
                self._document_ids = [row['id'] for row in rows]
                
                def tokenize(text):
                    return jieba.lcut(text)
                
                self._tfidf_vectorizer = TfidfVectorizer(
                    tokenizer=tokenize,
                    stop_words=None,
                    max_features=5000,
                    ngram_range=(1, 2)
                )
                self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(documents)
                
                logger.debug(f"TF-IDF index built with {len(documents)} documents")
                
        except Exception as e:
            logger.error(f"Failed to build TF-IDF index: {e}")
            self._tfidf_vectorizer = None
            self._tfidf_matrix = None
    
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
            knowledge_id = f"kb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            title = knowledge_data.get("title", knowledge_data.get("name", ""))
            data_json = json.dumps(knowledge_data, ensure_ascii=False)
            keywords = self._extract_keywords(knowledge_data)
            full_text = self._generate_full_text(knowledge_data)
            
            embedding = self._create_embedding(full_text)
            embedding_json = json.dumps(embedding) if embedding else None
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                    (category, "", format_timestamp()))
                
                cursor.execute('INSERT INTO knowledge (id, category, title, data, keywords, full_text, embedding, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (knowledge_id, category, title, data_json, keywords, full_text, embedding_json, format_timestamp(), format_timestamp()))
                
                conn.commit()
            
            self._ensure_tfidf_index()
            
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
        Import knowledge from various file formats (MD, DOCX, PDF, TXT, JSON)
        
        Args:
            file_path: Path to the file containing knowledge data
            category: Category of the knowledge
            
        Returns:
            Import result
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()
            
            if ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)
                return self.import_knowledge(knowledge_data, category)
            
            if not FILE_PARSER_AVAILABLE:
                raise ImportError("File parser module not available")
            
            parser = FileParser()
            parsed_result = parser.parse_file(file_path)
            
            imported_count = 0
            skipped_count = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                conn.execute("BEGIN TRANSACTION")
                
                try:
                    cursor.execute('INSERT OR IGNORE INTO categories (name, description, created_at) VALUES (?, ?, ?)',
                        (category, "", format_timestamp()))
                    
                    for entry in parsed_result.get("entries", []):
                        try:
                            knowledge_id = f"kb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                            entry_title = entry.get("title", parsed_result.get("title", "Untitled"))
                            entry_category = entry.get("category", category)
                            entry_content = entry.get("content", "")
                            entry_keywords = entry.get("keywords", "")
                            
                            if not entry_content:
                                skipped_count += 1
                                continue
                            
                            knowledge_data = {
                                "title": entry_title,
                                "content": entry_content,
                                "category": entry_category,
                                "keywords": entry_keywords
                            }
                            
                            data_json = json.dumps(knowledge_data, ensure_ascii=False)
                            keywords = self._extract_keywords(knowledge_data)
                            full_text = self._generate_full_text(knowledge_data)
                            
                            embedding = self._create_embedding(full_text)
                            embedding_json = json.dumps(embedding) if embedding else None
                            
                            cursor.execute('INSERT INTO knowledge (id, category, title, data, keywords, full_text, embedding, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                                (knowledge_id, entry_category, entry_title, data_json, keywords, full_text, embedding_json, format_timestamp(), format_timestamp()))
                            
                            imported_count += 1
                            
                        except Exception as e:
                            logger.warning(f"Skipping entry due to error: {e}")
                            skipped_count += 1
                            continue
                    
                    conn.commit()
                    
                    self._ensure_tfidf_index()
                    
                    logger.info(f"File import completed: {imported_count} imported, {skipped_count} skipped")
                    return {
                        "success": True,
                        "imported": imported_count,
                        "skipped": skipped_count,
                        "file_name": parsed_result.get("file_name"),
                        "file_format": parsed_result.get("format"),
                        "message": f"Successfully imported {imported_count} entries from file"
                    }
                
                except Exception as e:
                    conn.rollback()
                    logger.error(f"File import failed, rolled back: {e}")
                    raise KnowledgeBaseException(f"File import failed: {e}")
            
        except json.JSONDecodeError as e:
            raise KnowledgeBaseException(f"Invalid JSON file: {e}")
        except Exception as e:
            raise KnowledgeBaseException(f"Failed to import from file: {e}")
    
    def query_knowledge(self, query: str, category: Optional[str] = None, 
                       limit: int = 5, use_tfidf: bool = True) -> List[Dict[str, Any]]:
        """
        Query knowledge base with enhanced search
        
        Args:
            query: Search query string
            category: Filter by category (optional)
            limit: Maximum number of results
            use_tfidf: Use TF-IDF search (default True, fallback when vector unavailable)
            
        Returns:
            List of matching knowledge entries sorted by relevance
        """
        if EMBEDDING_AVAILABLE and self._embedding_client:
            return self._query_vector(query, category, limit)
        elif TF_IDF_AVAILABLE and use_tfidf:
            return self._query_tfidf(query, category, limit)
        else:
            return self._query_basic(query, category, limit)
    
    def _query_vector(self, query: str, category: Optional[str] = None,
                     limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query knowledge base using vector embedding similarity
        
        Args:
            query: Search query string
            category: Filter by category (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge entries sorted by relevance
        """
        try:
            query_embedding = self._create_embedding(query)
            if not query_embedding:
                logger.warning("Failed to create query embedding, falling back to TF-IDF")
                return self._query_tfidf(query, category, limit)
            
            results = []
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if category:
                    cursor.execute('SELECT * FROM knowledge WHERE category = ? AND embedding IS NOT NULL',
                        (category,))
                else:
                    cursor.execute('SELECT * FROM knowledge WHERE embedding IS NOT NULL')
                
                for row in cursor.fetchall():
                    try:
                        embedding = json.loads(row['embedding'])
                        if not embedding:
                            continue
                        
                        similarity = self._calculate_vector_similarity(query_embedding, embedding)
                        
                        if similarity < 0.01:
                            continue
                        
                        data = json.loads(row['data'])
                        results.append({
                            "id": row['id'],
                            "category": row['category'],
                            "title": row['title'],
                            "data": data,
                            "relevance": round(similarity * 100, 2),
                            "created_at": row['created_at']
                        })
                    except Exception as e:
                        logger.warning(f"Failed to process knowledge entry: {e}")
                        continue
            
            results.sort(key=lambda x: x["relevance"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return self._query_tfidf(query, category, limit)
    
    def _query_tfidf(self, query: str, category: Optional[str] = None, 
                    limit: int = 5) -> List[Dict[str, Any]]:
        """
        Query knowledge base using TF-IDF algorithm
        
        Args:
            query: Search query string
            category: Filter by category (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge entries sorted by relevance
        """
        self._ensure_tfidf_index()
        
        if not self._tfidf_vectorizer or not self._document_ids:
            return self._query_basic(query, category, limit)
        
        try:
            query_vec = self._tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
            
            ranked_indices = np.argsort(similarities)[::-1]
            
            results = []
            seen_ids = set()
            
            for idx in ranked_indices:
                if len(results) >= limit:
                    break
                
                doc_id = self._document_ids[idx]
                similarity = float(similarities[idx])
                
                if similarity < 0.01:
                    continue
                
                entry = self.get_knowledge_by_id(doc_id)
                if not entry:
                    continue
                
                if category and entry["category"] != category:
                    continue
                
                if doc_id in seen_ids:
                    continue
                
                seen_ids.add(doc_id)
                results.append({
                    "id": entry["id"],
                    "category": entry["category"],
                    "title": entry["title"],
                    "data": entry["data"],
                    "relevance": round(similarity * 100, 2),
                    "created_at": entry["created_at"]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"TF-IDF query failed: {e}")
            return self._query_basic(query, category, limit)
    
    def _query_basic(self, query: str, category: Optional[str] = None, 
                    limit: int = 5) -> List[Dict[str, Any]]:
        """
        Basic query using string matching (fallback)
        
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
                    cursor.execute('SELECT * FROM knowledge WHERE category = ?',
                        (category,))
                else:
                    cursor.execute('SELECT * FROM knowledge')
                
                for row in cursor.fetchall():
                    data = json.loads(row['data'])
                    data_str = json.dumps(data, ensure_ascii=False).lower()
                    full_text = row['full_text'].lower() if row['full_text'] else ""
                    
                    query_words = set(query_lower.split())
                    content_words = set(data_str.split()) | set(full_text.split())
                    
                    has_match = any(word in data_str or word in full_text for word in query_words)
                    
                    if has_match:
                        relevance = self._calculate_relevance(query_lower, data_str + " " + full_text)
                        results.append({
                            "id": row['id'],
                            "category": row['category'],
                            "title": row['title'],
                            "data": data,
                            "relevance": round(relevance * 100, 2),
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

    def get_all_knowledge(self, category: Optional[str] = None,
                          page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get all knowledge entries with pagination
        
        Args:
            category: Filter by category
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with data and pagination info
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM knowledge'
                params = []
                
                if category:
                    query += ' WHERE category = ?'
                    params.append(category)
                
                # Get total count
                count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
                total = cursor.execute(count_query, params).fetchone()[0]
                
                # Get paginated results
                query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
                params.extend([per_page, (page - 1) * per_page])
                
                rows = cursor.execute(query, params).fetchall()
                
                data = []
                for row in rows:
                    entry = {
                        "id": row['id'],
                        "category": row['category'],
                        "title": row['title'],
                        "created_at": row['created_at'],
                        "updated_at": row['updated_at']
                    }
                    try:
                        entry["data"] = json.loads(row['data'])
                        entry["content"] = entry["data"].get("content", "")
                    except:
                        entry["data"] = {}
                        entry["content"] = ""
                    data.append(entry)
                
                return {
                    "success": True,
                    "data": data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": total,
                        "pages": (total + per_page - 1) // per_page
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get all knowledge: {e}")
            return {"success": False, "error": str(e), "data": [], "pagination": {"page": page, "per_page": per_page, "total": 0, "pages": 0}}
    
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
            full_text = self._generate_full_text(new_data)
            title = new_data.get("title", new_data.get("name", ""))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('UPDATE knowledge SET data = ?, title = ?, keywords = ?, full_text = ?, updated_at = ? WHERE id = ?',
                    (data_json, title, keywords, full_text, format_timestamp(), knowledge_id))
                
                if cursor.rowcount == 0:
                    raise KnowledgeBaseException(f"Knowledge ID not found: {knowledge_id}")
                
                conn.commit()
            
            self._ensure_tfidf_index()
            
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
            
            self._ensure_tfidf_index()
            
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
                    "last_updated": format_timestamp(),
                    "tfidf_available": TF_IDF_AVAILABLE
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "total_entries": 0,
                "categories": {},
                "category_count": 0,
                "last_updated": format_timestamp(),
                "tfidf_available": TF_IDF_AVAILABLE
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
    
    def refresh_search_index(self):
        """Refresh the TF-IDF search index"""
        self._ensure_tfidf_index()
        return {
            "success": True,
            "message": "Search index refreshed",
            "tfidf_available": TF_IDF_AVAILABLE
        }
