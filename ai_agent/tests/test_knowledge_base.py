"""
Unit tests for knowledge base module
"""
import pytest
import tempfile
import os
import shutil
from knowledge_base import KnowledgeBase


class TestKnowledgeBase:
    """Tests for KnowledgeBase class"""

    @pytest.fixture
    def temp_kb(self):
        """Create a temporary knowledge base for testing"""
        temp_dir = tempfile.mkdtemp()
        temp_db = os.path.join(temp_dir, "test_kb.db")
        kb = KnowledgeBase(db_path=temp_db)
        yield kb
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_initialization(self, temp_kb):
        """Test knowledge base initialization"""
        assert temp_kb is not None
        stats = temp_kb.get_statistics()
        assert stats["total_entries"] == 0

    def test_import_knowledge(self, temp_kb):
        """Test importing knowledge"""
        test_data = {
            "title": "Test Dog Care",
            "content": {"breed": "Golden Retriever", "care": "Needs daily exercise"},
            "category": "dogs"
        }
        
        result = temp_kb.import_knowledge(test_data, category="dogs")
        assert result["success"] is True
        assert "knowledge_id" in result
        
        stats = temp_kb.get_statistics()
        assert stats["total_entries"] == 1

    def test_query_knowledge(self, temp_kb):
        """Test knowledge query"""
        # First add some test data
        test_data1 = {
            "title": "Golden Retriever Care",
            "content": {"breed": "Golden Retriever", "activity_level": "high"}
        }
        test_data2 = {
            "title": "Cat Health",
            "content": {"species": "Cat", "vaccinations": ["FVRCP", "Rabies"]}
        }
        
        temp_kb.import_knowledge(test_data1, category="dogs")
        temp_kb.import_knowledge(test_data2, category="cats")
        
        # Query for dog-related content
        results = temp_kb.query_knowledge("Golden Retriever")
        assert len(results) >= 1
        
        # Query for cat-related content
        results = temp_kb.query_knowledge("Cat")
        assert len(results) >= 1

    def test_get_knowledge_by_id(self, temp_kb):
        """Test getting knowledge by ID"""
        test_data = {"title": "Test Entry", "content": {"key": "value"}}
        result = temp_kb.import_knowledge(test_data, category="test")
        
        knowledge_id = result["knowledge_id"]
        entry = temp_kb.get_knowledge_by_id(knowledge_id)
        
        assert entry is not None
        assert entry["id"] == knowledge_id
        assert entry["title"] == "Test Entry"

    def test_update_knowledge(self, temp_kb):
        """Test updating knowledge"""
        # Add initial entry
        test_data = {"title": "Original Title", "content": {"value": "original"}}
        result = temp_kb.import_knowledge(test_data, category="test")
        knowledge_id = result["knowledge_id"]
        
        # Update entry
        updated_data = {"title": "Updated Title", "content": {"value": "updated"}}
        update_result = temp_kb.update_knowledge(knowledge_id, updated_data)
        
        assert update_result["success"] is True
        
        # Verify update
        entry = temp_kb.get_knowledge_by_id(knowledge_id)
        assert entry["title"] == "Updated Title"

    def test_delete_knowledge(self, temp_kb):
        """Test deleting knowledge"""
        test_data = {"title": "To Be Deleted", "content": {"value": "delete me"}}
        result = temp_kb.import_knowledge(test_data, category="test")
        knowledge_id = result["knowledge_id"]
        
        # Verify it exists
        assert temp_kb.get_knowledge_by_id(knowledge_id) is not None
        
        # Delete it
        delete_result = temp_kb.delete_knowledge(knowledge_id)
        assert delete_result["success"] is True
        
        # Verify it's gone
        assert temp_kb.get_knowledge_by_id(knowledge_id) is None

    def test_get_categories(self, temp_kb):
        """Test getting categories"""
        temp_kb.import_knowledge({"title": "Dog Info"}, category="dogs")
        temp_kb.import_knowledge({"title": "Cat Info"}, category="cats")
        
        categories = temp_kb.get_all_categories()
        assert "dogs" in categories
        assert "cats" in categories

    def test_get_statistics(self, temp_kb):
        """Test getting statistics"""
        for i in range(5):
            temp_kb.import_knowledge(
                {"title": f"Entry {i}"}, 
                category="test"
            )
        
        stats = temp_kb.get_statistics()
        assert stats["total_entries"] == 5
        assert stats["category_count"] >= 1