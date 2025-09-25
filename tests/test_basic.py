"""
Basic pytest tests for CodeCraft AI platform
"""
import pytest
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_basic_functionality():
    """Test that basic Python functionality works"""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    
def test_environment_setup():
    """Test that required packages are available"""
    try:
        import requests
        assert requests.__version__ is not None
    except ImportError:
        pytest.fail("requests package not available")
    
    try:
        import fastapi
        assert fastapi.__version__ is not None
    except ImportError:
        pytest.fail("FastAPI package not available")

def test_backend_imports():
    """Test that backend modules can be imported"""
    try:
        # Test if server.py can be imported (basic syntax check)
        import server
        assert hasattr(server, 'app')
        assert hasattr(server, 'SQLToSnowflakeConverter')
        assert hasattr(server, 'ERDiagramParser')
        assert hasattr(server, 'AIAssistant')
    except ImportError as e:
        pytest.fail(f"Backend server.py import failed: {e}")
    except Exception as e:
        pytest.fail(f"Backend server.py has issues: {e}")

class TestSQLConverter:
    """Test SQL converter functionality"""
    
    def test_converter_initialization(self):
        """Test that SQL converter can be initialized"""
        from server import SQLToSnowflakeConverter
        converter = SQLToSnowflakeConverter()
        assert converter is not None
        assert hasattr(converter, 'data_type_mappings')
        assert 'mysql' in converter.data_type_mappings
        assert 'postgresql' in converter.data_type_mappings
        assert 'sqlserver' in converter.data_type_mappings
        assert 'oracle' in converter.data_type_mappings

class TestERDiagramParser:
    """Test ER diagram parser functionality"""
    
    def test_parser_initialization(self):
        """Test that ER diagram parser can be initialized"""
        from server import ERDiagramParser
        parser = ERDiagramParser()
        assert parser is not None
        assert hasattr(parser, 'parse_sql_to_er')
        
    def test_basic_sql_parsing(self):
        """Test basic SQL parsing functionality"""
        from server import ERDiagramParser
        parser = ERDiagramParser()
        
        # Test basic CREATE TABLE parsing
        simple_sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));"
        result = parser.parse_sql_to_er(simple_sql, "mysql")
        
        assert result is not None
        assert hasattr(result, 'tables')
        assert hasattr(result, 'relationships')
        assert result.database_type == "mysql"

class TestAIAssistant:
    """Test AI assistant functionality"""
    
    def test_assistant_initialization(self):
        """Test that AI assistant can be initialized"""
        from server import AIAssistant
        assistant = AIAssistant()
        assert assistant is not None
        assert hasattr(assistant, 'available_models')
        assert 'openai' in assistant.available_models
        assert 'anthropic' in assistant.available_models
        assert 'gemini' in assistant.available_models