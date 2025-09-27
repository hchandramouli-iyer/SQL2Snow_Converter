#!/usr/bin/env python3
"""
Comprehensive Backend Testing Suite for CodeCraft AI Platform
Tests all core functionality after repository cleanup and restructuring
"""

import requests
import json
import time
import uuid
from typing import Dict, List, Any
import tempfile
import os

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = "https://codecraft-ai-20.preview.emergentagent.com/api"
        self.session = requests.Session()
        self.test_results = []
        self.session_id = str(uuid.uuid4())
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root Endpoint", True, f"Status: {response.status_code}, Message: {data['message']}")
                    return True
            self.log_test("Root Endpoint", False, f"Unexpected response: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_sql_conversion_text(self):
        """Test SQL text conversion endpoint"""
        try:
            # Test MySQL to Snowflake conversion
            test_sql = """
            CREATE TABLE ecommerce_users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            """
            
            payload = {
                "sql_content": test_sql,
                "source_database": "mysql",
                "source_database_name": "ecommerce_db",
                "source_schema_name": "public",
                "target_database_name": "ANALYTICS_DW",
                "target_schema_name": "STAGING",
                "custom_instructions": "Optimize for analytics workload",
                "include_comments": True,
                "preserve_case": False
            }
            
            response = self.session.post(f"{self.base_url}/convert", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "converted_sql" in data and "ANALYTICS_DW.STAGING" in data["converted_sql"]:
                    self.log_test("SQL Text Conversion (MySQL)", True, 
                                f"Successfully converted MySQL to Snowflake with proper qualification")
                    return True
            self.log_test("SQL Text Conversion (MySQL)", False, 
                        f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
        except Exception as e:
            self.log_test("SQL Text Conversion (MySQL)", False, f"Exception: {str(e)}")
            return False
    
    def test_sql_conversion_other_databases(self):
        """Test SQL conversion for other database types"""
        databases = [
            ("postgresql", "SELECT * FROM users WHERE created_at > NOW();"),
            ("sqlserver", "SELECT GETDATE() as current_time, [user_id] FROM [users];"),
            ("oracle", "SELECT SYSDATE FROM DUAL;")
        ]
        
        success_count = 0
        for db_type, test_sql in databases:
            try:
                payload = {
                    "sql_content": test_sql,
                    "source_database": db_type,
                    "target_database_name": "DW_ANALYTICS",
                    "target_schema_name": "PROD"
                }
                
                response = self.session.post(f"{self.base_url}/convert", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if "converted_sql" in data:
                        self.log_test(f"SQL Conversion ({db_type.upper()})", True, 
                                    f"Successfully converted {db_type} to Snowflake")
                        success_count += 1
                    else:
                        self.log_test(f"SQL Conversion ({db_type.upper()})", False, 
                                    "Missing converted_sql in response")
                else:
                    self.log_test(f"SQL Conversion ({db_type.upper()})", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"SQL Conversion ({db_type.upper()})", False, f"Exception: {str(e)}")
        
        return success_count == len(databases)
    
    def test_sql_file_conversion(self):
        """Test SQL file conversion endpoint"""
        try:
            # Create a temporary SQL file
            test_sql = """
            CREATE TABLE products (
                product_id INT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2),
                category_id INT,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            );
            
            CREATE TABLE categories (
                category_id INT PRIMARY KEY,
                category_name VARCHAR(50) NOT NULL
            );
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                temp_file.write(test_sql)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as file:
                    files = {'file': ('test.sql', file, 'text/plain')}
                    data = {
                        'source_database': 'mysql',
                        'target_database_name': 'ANALYTICS_DW',
                        'target_schema_name': 'STAGING'
                    }
                    
                    response = self.session.post(f"{self.base_url}/convert-file", files=files, data=data)
                    if response.status_code == 200:
                        result = response.json()
                        if "converted_sql" in result and "ANALYTICS_DW.STAGING" in result["converted_sql"]:
                            self.log_test("SQL File Conversion", True, 
                                        "Successfully converted SQL file with proper qualification")
                            return True
                    self.log_test("SQL File Conversion", False, 
                                f"Status: {response.status_code}, Response: {response.text[:200]}")
                    return False
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("SQL File Conversion", False, f"Exception: {str(e)}")
            return False
    
    def test_er_diagram_generation(self):
        """Test ER diagram generation from SQL text"""
        try:
            test_sql = """
            CREATE TABLE customers (
                customer_id INT PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(20)
            );
            
            CREATE TABLE orders (
                order_id INT PRIMARY KEY,
                customer_id INT,
                order_date DATE,
                total_amount DECIMAL(10,2),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            """
            
            payload = {
                "sql_content": test_sql,
                "database_type": "mysql"
            }
            
            response = self.session.post(f"{self.base_url}/er-diagram/generate", json=payload)
            if response.status_code == 200:
                data = response.json()
                if ("tables" in data and len(data["tables"]) == 2 and 
                    "relationships" in data and len(data["relationships"]) >= 1):
                    self.log_test("ER Diagram Generation", True, 
                                f"Generated ER diagram with {len(data['tables'])} tables and {len(data['relationships'])} relationships")
                    return True
            self.log_test("ER Diagram Generation", False, 
                        f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
        except Exception as e:
            self.log_test("ER Diagram Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_er_diagram_file_generation(self):
        """Test ER diagram generation from SQL file"""
        try:
            test_sql = """
            CREATE TABLE users (
                user_id INT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100)
            );
            
            CREATE TABLE posts (
                post_id INT PRIMARY KEY,
                user_id INT,
                title VARCHAR(200),
                content TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            
            CREATE TABLE comments (
                comment_id INT PRIMARY KEY,
                post_id INT,
                user_id INT,
                comment_text TEXT,
                FOREIGN KEY (post_id) REFERENCES posts(post_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
                temp_file.write(test_sql)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as file:
                    files = {'file': ('er_test.sql', file, 'text/plain')}
                    data = {'database_type': 'mysql'}
                    
                    response = self.session.post(f"{self.base_url}/er-diagram/generate-file", 
                                               files=files, data=data)
                    if response.status_code == 200:
                        result = response.json()
                        if ("tables" in result and len(result["tables"]) == 3 and 
                            "relationships" in result and len(result["relationships"]) >= 2):
                            self.log_test("ER Diagram File Generation", True, 
                                        f"Generated ER diagram from file with {len(result['tables'])} tables and {len(result['relationships'])} relationships")
                            return True
                    self.log_test("ER Diagram File Generation", False, 
                                f"Status: {response.status_code}, Response: {response.text[:200]}")
                    return False
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_test("ER Diagram File Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_tools_processing(self):
        """Test all AI tools processing endpoints"""
        ai_tools = [
            ("code_generator", "Create a Python function to calculate fibonacci numbers", "python"),
            ("code_assistant", "Help me fix this Python code: def add(a, b): return a + b + c", "python"),
            ("code_converter", "Convert this Python code to JavaScript: print('Hello World')", "python", "javascript"),
            ("code_explainer", "def quicksort(arr): return arr if len(arr) <= 1 else quicksort([x for x in arr[1:] if x < arr[0]]) + [arr[0]] + quicksort([x for x in arr[1:] if x >= arr[0]])", "python"),
            ("code_enhancer", "def calculate_total(items): total = 0; for item in items: total += item; return total", "python"),
            ("comment_generator", "def binary_search(arr, target): left, right = 0, len(arr) - 1; while left <= right: mid = (left + right) // 2; if arr[mid] == target: return mid; elif arr[mid] < target: left = mid + 1; else: right = mid - 1; return -1", "python"),
            ("unit_test_generator", "def is_prime(n): if n < 2: return False; for i in range(2, int(n**0.5) + 1): if n % i == 0: return False; return True", "python")
        ]
        
        success_count = 0
        for tool_data in ai_tools:
            tool_type = tool_data[0]
            content = tool_data[1]
            language = tool_data[2]
            target_language = tool_data[3] if len(tool_data) > 3 else None
            
            try:
                payload = {
                    "tool_type": tool_type,
                    "content": content,
                    "language": language,
                    "llm_provider": "openai",
                    "llm_model": "gpt-4o-mini"
                }
                
                if target_language:
                    payload["target_language"] = target_language
                
                response = self.session.post(f"{self.base_url}/ai/process", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if "generated_content" in data and len(data["generated_content"]) > 10:
                        self.log_test(f"AI Tool ({tool_type})", True, 
                                    f"Successfully processed {tool_type} request")
                        success_count += 1
                    else:
                        self.log_test(f"AI Tool ({tool_type})", False, 
                                    "Generated content too short or missing")
                else:
                    self.log_test(f"AI Tool ({tool_type})", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"AI Tool ({tool_type})", False, f"Exception: {str(e)}")
        
        return success_count >= len(ai_tools) * 0.8  # 80% success rate acceptable
    
    def test_chat_functionality(self):
        """Test chat system endpoints"""
        success_count = 0
        
        # Test main chat endpoint
        try:
            payload = {
                "tool_type": "chat",
                "content": "Hello! Can you help me with Python programming?",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
                "session_id": self.session_id
            }
            
            response = self.session.post(f"{self.base_url}/ai/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "response" in data and len(data["response"]) > 10:
                    self.log_test("Chat Endpoint", True, "Successfully received chat response")
                    success_count += 1
                else:
                    self.log_test("Chat Endpoint", False, "Chat response too short or missing")
            else:
                self.log_test("Chat Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Chat Endpoint", False, f"Exception: {str(e)}")
        
        # Test simple chat endpoint
        try:
            data = {
                "content": "What is machine learning?",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
                "session_id": self.session_id
            }
            
            response = self.session.post(f"{self.base_url}/ai/chat-simple", data=data)
            if response.status_code == 200:
                result = response.json()
                if "response" in result and len(result["response"]) > 10:
                    self.log_test("Chat Simple Endpoint", True, "Successfully received simple chat response")
                    success_count += 1
                else:
                    self.log_test("Chat Simple Endpoint", False, "Simple chat response too short or missing")
            else:
                self.log_test("Chat Simple Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Chat Simple Endpoint", False, f"Exception: {str(e)}")
        
        # Test chat history endpoint
        try:
            time.sleep(1)  # Give time for chat messages to be saved
            response = self.session.get(f"{self.base_url}/ai/chat-history/{self.session_id}")
            if response.status_code == 200:
                history = response.json()
                if isinstance(history, list) and len(history) >= 1:
                    self.log_test("Chat History Endpoint", True, 
                                f"Successfully retrieved {len(history)} chat messages")
                    success_count += 1
                else:
                    self.log_test("Chat History Endpoint", False, "No chat history found")
            else:
                self.log_test("Chat History Endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Chat History Endpoint", False, f"Exception: {str(e)}")
        
        return success_count >= 2  # At least 2 out of 3 chat tests should pass
    
    def test_models_endpoint(self):
        """Test available models endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/ai/models")
            if response.status_code == 200:
                data = response.json()
                if ("models" in data and "openai" in data["models"] and 
                    "anthropic" in data["models"] and "gemini" in data["models"]):
                    model_count = sum(len(models) for models in data["models"].values())
                    self.log_test("Models Endpoint", True, 
                                f"Successfully retrieved {model_count} models from 3 providers")
                    return True
            self.log_test("Models Endpoint", False, 
                        f"Status: {response.status_code}, Response: {response.text[:200]}")
            return False
        except Exception as e:
            self.log_test("Models Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_file_download(self):
        """Test file download functionality"""
        try:
            # First create a conversion to get an ID for download
            test_sql = "CREATE TABLE test_table (id INT PRIMARY KEY, name VARCHAR(50));"
            payload = {
                "sql_content": test_sql,
                "source_database": "mysql"
            }
            
            response = self.session.post(f"{self.base_url}/convert", json=payload)
            if response.status_code == 200:
                conversion_data = response.json()
                conversion_id = conversion_data.get("id")
                
                if conversion_id:
                    # Test download
                    download_response = self.session.get(f"{self.base_url}/download/{conversion_id}")
                    if download_response.status_code == 200:
                        if len(download_response.content) > 0:
                            self.log_test("File Download", True, 
                                        f"Successfully downloaded SQL file ({len(download_response.content)} bytes)")
                            return True
                    self.log_test("File Download", False, 
                                f"Download failed with status: {download_response.status_code}")
                else:
                    self.log_test("File Download", False, "No conversion ID returned for download test")
            else:
                self.log_test("File Download", False, "Failed to create conversion for download test")
            return False
        except Exception as e:
            self.log_test("File Download", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive Backend Testing Suite")
        print("=" * 60)
        
        test_functions = [
            self.test_root_endpoint,
            self.test_sql_conversion_text,
            self.test_sql_conversion_other_databases,
            self.test_sql_file_conversion,
            self.test_er_diagram_generation,
            self.test_er_diagram_file_generation,
            self.test_ai_tools_processing,
            self.test_chat_functionality,
            self.test_models_endpoint,
            self.test_file_download
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_func.__name__}: {str(e)}")
        
        print("\n" + "=" * 60)
        print("📊 BACKEND TESTING SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is fully functional after cleanup!")
        elif success_rate >= 80:
            print("✅ GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 60:
            print("⚠️  WARNING: Backend has significant issues that need attention")
        else:
            print("🚨 CRITICAL: Backend has major functionality problems")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)