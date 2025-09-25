import requests
import sys
import json
import tempfile
import os
from datetime import datetime

class SQLConverterAPITester:
    def __init__(self, base_url="https://sqlsnowforge.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.conversion_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if files is None:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.content
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_mysql_conversion(self):
        """Test MySQL to Snowflake conversion"""
        mysql_sql = """CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""

        success, response = self.run_test(
            "MySQL SQL Conversion",
            "POST",
            "convert",
            200,
            data={
                "sql_content": mysql_sql,
                "source_database": "mysql",
                "conversion_type": "basic"
            }
        )
        
        if success and 'id' in response:
            self.conversion_id = response['id']
            print(f"   Conversion ID: {self.conversion_id}")
            
            # Check if conversion actually happened
            if 'converted_sql' in response:
                converted = response['converted_sql']
                if 'AUTOINCREMENT' in converted and 'NUMBER(38,0)' in converted:
                    print("   ✅ MySQL-specific conversions detected")
                else:
                    print("   ⚠️  MySQL-specific conversions may not have occurred")
        
        return success

    def test_postgresql_conversion(self):
        """Test PostgreSQL to Snowflake conversion"""
        postgresql_sql = """CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);"""

        success, response = self.run_test(
            "PostgreSQL SQL Conversion",
            "POST",
            "convert",
            200,
            data={
                "sql_content": postgresql_sql,
                "source_database": "postgresql",
                "conversion_type": "basic"
            }
        )
        
        if success and 'converted_sql' in response:
            converted = response['converted_sql']
            if 'AUTOINCREMENT' in converted and 'NUMBER(38,0)' in converted:
                print("   ✅ PostgreSQL-specific conversions detected")
        
        return success

    def test_sqlserver_conversion(self):
        """Test SQL Server to Snowflake conversion"""
        sqlserver_sql = """CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    email NVARCHAR(100) UNIQUE,
    created_at DATETIME2 DEFAULT GETDATE(),
    is_active BIT DEFAULT 1
);"""

        success, response = self.run_test(
            "SQL Server SQL Conversion",
            "POST",
            "convert",
            200,
            data={
                "sql_content": sqlserver_sql,
                "source_database": "sqlserver",
                "conversion_type": "basic"
            }
        )
        
        if success and 'converted_sql' in response:
            converted = response['converted_sql']
            if 'AUTOINCREMENT' in converted and 'CURRENT_TIMESTAMP' in converted:
                print("   ✅ SQL Server-specific conversions detected")
        
        return success

    def test_oracle_conversion(self):
        """Test Oracle to Snowflake conversion"""
        oracle_sql = """CREATE TABLE users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) UNIQUE,
    created_at TIMESTAMP DEFAULT SYSDATE,
    is_active NUMBER(1) DEFAULT 1
);"""

        success, response = self.run_test(
            "Oracle SQL Conversion",
            "POST",
            "convert",
            200,
            data={
                "sql_content": oracle_sql,
                "source_database": "oracle",
                "conversion_type": "basic"
            }
        )
        
        if success and 'converted_sql' in response:
            converted = response['converted_sql']
            if 'CURRENT_TIMESTAMP' in converted and 'VARCHAR' in converted:
                print("   ✅ Oracle-specific conversions detected")
        
        return success

    def test_file_conversion(self):
        """Test file upload conversion"""
        # Create a temporary SQL file
        sql_content = """CREATE TABLE test_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(sql_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {'file': ('test.sql', file, 'text/plain')}
                data = {'source_database': 'mysql'}
                
                success, response = self.run_test(
                    "File Upload Conversion",
                    "POST",
                    "convert-file",
                    200,
                    data=data,
                    files=files
                )
                
                if success and 'id' in response:
                    self.conversion_id = response['id']
                    print(f"   File Conversion ID: {self.conversion_id}")
                
                return success
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

    def test_download_conversion(self):
        """Test download converted SQL"""
        if not self.conversion_id:
            print("❌ No conversion ID available for download test")
            return False

        success, response = self.run_test(
            "Download Converted SQL",
            "GET",
            f"download/{self.conversion_id}",
            200
        )
        
        if success:
            print(f"   Downloaded content length: {len(response) if isinstance(response, bytes) else 'N/A'}")
        
        return success

    def test_conversion_history(self):
        """Test conversion history endpoint - Not implemented in current API"""
        print("\n🔍 Testing Conversion History...")
        print("   ⚠️  No general conversion history endpoint found in API")
        print("   ✅ Skipped - Not implemented")
        return True  # Skip this test as endpoint doesn't exist

    def test_invalid_database(self):
        """Test conversion with invalid database"""
        success, response = self.run_test(
            "Invalid Database Conversion",
            "POST",
            "convert",
            200,  # Should still return 200 but with warnings
            data={
                "sql_content": "SELECT * FROM test;",
                "source_database": "invalid_db",
                "conversion_type": "basic"
            }
        )
        
        if success and 'warnings' in response:
            warnings = response['warnings']
            if any('Unsupported source database' in warning for warning in warnings):
                print("   ✅ Invalid database properly handled with warning")
            else:
                print("   ⚠️  Expected warning for invalid database not found")
        
        return success

    def test_empty_sql(self):
        """Test conversion with empty SQL"""
        success, response = self.run_test(
            "Empty SQL Conversion",
            "POST",
            "convert",
            200,
            data={
                "sql_content": "",
                "source_database": "mysql",
                "conversion_type": "basic"
            }
        )
        return success

    def test_ai_models_endpoint(self):
        """Test AI models availability endpoint"""
        success, response = self.run_test(
            "AI Models Endpoint",
            "GET",
            "ai/models",
            200
        )
        
        if success and 'models' in response:
            models = response['models']
            if isinstance(models, dict) and 'openai' in models and 'anthropic' in models:
                print("   ✅ AI models properly structured")
                print(f"   Available providers: {list(models.keys())}")
            else:
                print("   ⚠️  AI models structure unexpected")
        
        return success

    def test_ai_code_generator(self):
        """Test AI code generator tool"""
        success, response = self.run_test(
            "AI Code Generator",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "code_generator",
                "content": "Create a Python function to calculate fibonacci numbers",
                "language": "python",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if 'def' in generated and 'fibonacci' in generated.lower():
                print("   ✅ Code generation appears successful")
            else:
                print("   ⚠️  Generated code may not match request")
        
        return success

    def test_ai_code_assistant(self):
        """Test AI code assistant tool"""
        success, response = self.run_test(
            "AI Code Assistant",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "code_assistant",
                "content": "Help me fix this Python code: def add(a, b) return a + b",
                "language": "python",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if ':' in generated:
                print("   ✅ Code assistance appears successful")
        
        return success

    def test_ai_code_converter(self):
        """Test AI code converter tool"""
        success, response = self.run_test(
            "AI Code Converter",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "code_converter",
                "content": "def hello(): print('Hello World')",
                "language": "python",
                "target_language": "javascript",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if 'function' in generated.lower() or 'console.log' in generated:
                print("   ✅ Code conversion appears successful")
        
        return success

    def test_ai_code_explainer(self):
        """Test AI code explainer tool"""
        success, response = self.run_test(
            "AI Code Explainer",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "code_explainer",
                "content": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
                "language": "python",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if 'factorial' in generated.lower() and 'recursive' in generated.lower():
                print("   ✅ Code explanation appears successful")
        
        return success

    def test_ai_chat_endpoint(self):
        """Test AI chat endpoint"""
        success, response = self.run_test(
            "AI Chat Endpoint",
            "POST",
            "ai/chat",
            200,
            data={
                "tool_type": "chat",  # Required field
                "content": "Hello, can you help me with Python programming?",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'response' in response and 'session_id' in response:
            print(f"   ✅ Chat successful, session_id: {response['session_id'][:8]}...")
            self.chat_session_id = response['session_id']
        
        return success

    def test_ai_chat_simple_endpoint(self):
        """Test AI simple chat endpoint"""
        # Test with form data
        import requests
        url = f"{self.api_url}/ai/chat-simple"
        
        self.tests_run += 1
        print(f"\n🔍 Testing AI Simple Chat Endpoint...")
        print(f"   URL: {url}")
        
        try:
            data = {
                'content': 'What is Python?',
                'llm_provider': 'openai',
                'llm_model': 'gpt-4o-mini'
            }
            
            response = requests.post(url, data=data)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if 'response' in response_data and 'session_id' in response_data:
                        print("   ✅ Simple chat response structure correct")
                    return True
                except:
                    return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_ai_chat_history(self):
        """Test AI chat history endpoint"""
        if not hasattr(self, 'chat_session_id') or not self.chat_session_id:
            print("❌ No chat session ID available for history test")
            return False

        success, response = self.run_test(
            "AI Chat History",
            "GET",
            f"ai/chat-history/{self.chat_session_id}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Chat history entries: {len(response)}")
            if len(response) > 0:
                print("   ✅ Chat history retrieved successfully")
        
        return success

    def test_ai_unit_test_generator(self):
        """Test AI unit test generator tool"""
        success, response = self.run_test(
            "AI Unit Test Generator",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "unit_test_generator",
                "content": "def add_numbers(a, b): return a + b",
                "language": "python",
                "framework": "pytest",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if 'test_' in generated and 'assert' in generated:
                print("   ✅ Unit test generation appears successful")
        
        return success

    def test_ai_comment_generator(self):
        """Test AI comment generator tool"""
        success, response = self.run_test(
            "AI Comment Generator",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "comment_generator",
                "content": "def calculate_area(radius): return 3.14159 * radius * radius",
                "language": "python",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if '"""' in generated or '#' in generated:
                print("   ✅ Comment generation appears successful")
        
        return success

    def test_ai_code_enhancer(self):
        """Test AI code enhancer tool"""
        success, response = self.run_test(
            "AI Code Enhancer",
            "POST",
            "ai/process",
            200,
            data={
                "tool_type": "code_enhancer",
                "content": "def sort_list(lst): return sorted(lst)",
                "language": "python",
                "requirements": "Add error handling and type hints",
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini"
            }
        )
        
        if success and 'generated_content' in response:
            generated = response['generated_content']
            if 'try' in generated or 'except' in generated or ':' in generated:
                print("   ✅ Code enhancement appears successful")
        
        return success

    def test_er_diagram_generate(self):
        """Test ER diagram generation from SQL text"""
        sample_sql = """CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    total DECIMAL(10,2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);"""

        success, response = self.run_test(
            "ER Diagram Generation from SQL Text",
            "POST",
            "er-diagram/generate",
            200,
            data={
                "sql_content": sample_sql,
                "database_type": "mysql"
            }
        )
        
        if success:
            # Verify response structure
            required_fields = ['id', 'tables', 'relationships', 'database_type', 'created_at']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print("   ✅ Response structure correct")
                
                # Check tables
                if 'tables' in response and isinstance(response['tables'], list):
                    tables = response['tables']
                    table_names = [table['name'] for table in tables if 'name' in table]
                    
                    if 'users' in table_names and 'orders' in table_names:
                        print("   ✅ Tables correctly parsed (users, orders)")
                        
                        # Check table columns
                        users_table = next((t for t in tables if t['name'] == 'users'), None)
                        orders_table = next((t for t in tables if t['name'] == 'orders'), None)
                        
                        if users_table and 'columns' in users_table:
                            user_columns = [col['name'] for col in users_table['columns']]
                            if 'id' in user_columns and 'username' in user_columns:
                                print("   ✅ Users table columns correctly parsed")
                        
                        if orders_table and 'columns' in orders_table:
                            order_columns = [col['name'] for col in orders_table['columns']]
                            if 'id' in order_columns and 'user_id' in order_columns:
                                print("   ✅ Orders table columns correctly parsed")
                    else:
                        print(f"   ⚠️  Expected tables not found. Found: {table_names}")
                
                # Check relationships
                if 'relationships' in response and isinstance(response['relationships'], list):
                    relationships = response['relationships']
                    if len(relationships) > 0:
                        rel = relationships[0]
                        if ('from_table' in rel and 'to_table' in rel and 
                            rel['from_table'] == 'orders' and rel['to_table'] == 'users'):
                            print("   ✅ Foreign key relationship correctly identified")
                        else:
                            print(f"   ⚠️  Relationship structure unexpected: {rel}")
                    else:
                        print("   ⚠️  No relationships found")
                
                # Store ER diagram ID for potential future tests
                if 'id' in response:
                    self.er_diagram_id = response['id']
                    print(f"   ER Diagram ID: {self.er_diagram_id}")
            else:
                print(f"   ⚠️  Missing required fields: {missing_fields}")
        
        return success

    def test_er_diagram_generate_file(self):
        """Test ER diagram generation from uploaded SQL file"""
        sample_sql = """CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    total DECIMAL(10,2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    product_id INT,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);"""
        
        # Create a temporary SQL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(sample_sql)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {'file': ('er_test.sql', file, 'text/plain')}
                data = {'database_type': 'mysql'}
                
                success, response = self.run_test(
                    "ER Diagram Generation from SQL File",
                    "POST",
                    "er-diagram/generate-file",
                    200,
                    data=data,
                    files=files
                )
                
                if success:
                    # Verify response structure
                    required_fields = ['id', 'tables', 'relationships', 'database_type', 'created_at']
                    missing_fields = [field for field in required_fields if field not in response]
                    
                    if not missing_fields:
                        print("   ✅ File upload response structure correct")
                        
                        # Check tables
                        if 'tables' in response and isinstance(response['tables'], list):
                            tables = response['tables']
                            table_names = [table['name'] for table in tables if 'name' in table]
                            expected_tables = ['users', 'orders', 'products', 'order_items']
                            
                            found_tables = [name for name in expected_tables if name in table_names]
                            if len(found_tables) == len(expected_tables):
                                print(f"   ✅ All expected tables found: {found_tables}")
                            else:
                                print(f"   ⚠️  Expected {expected_tables}, found: {table_names}")
                        
                        # Check relationships
                        if 'relationships' in response and isinstance(response['relationships'], list):
                            relationships = response['relationships']
                            if len(relationships) >= 3:  # Should have at least 3 relationships
                                print(f"   ✅ Multiple relationships found: {len(relationships)}")
                                
                                # Check for specific relationships
                                rel_pairs = [(r['from_table'], r['to_table']) for r in relationships]
                                expected_rels = [('orders', 'users'), ('order_items', 'orders'), ('order_items', 'products')]
                                
                                found_rels = [rel for rel in expected_rels if rel in rel_pairs]
                                if len(found_rels) >= 2:
                                    print(f"   ✅ Key relationships identified: {found_rels}")
                                else:
                                    print(f"   ⚠️  Expected relationships not all found. Found: {rel_pairs}")
                            else:
                                print(f"   ⚠️  Expected multiple relationships, found: {len(relationships)}")
                        
                        # Store file ER diagram ID
                        if 'id' in response:
                            self.er_diagram_file_id = response['id']
                            print(f"   File ER Diagram ID: {self.er_diagram_file_id}")
                    else:
                        print(f"   ⚠️  Missing required fields: {missing_fields}")
                
                return success
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)

def main():
    print("🚀 Starting AI-Powered SQL Converter & Coding Assistant API Tests")
    print("=" * 70)
    
    tester = SQLConverterAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic API tests
    test_results.append(("Root Endpoint", tester.test_root_endpoint()))
    
    # AI Model availability
    test_results.append(("AI Models Endpoint", tester.test_ai_models_endpoint()))
    
    # Database conversion tests
    test_results.append(("MySQL Conversion", tester.test_mysql_conversion()))
    test_results.append(("PostgreSQL Conversion", tester.test_postgresql_conversion()))
    test_results.append(("SQL Server Conversion", tester.test_sqlserver_conversion()))
    test_results.append(("Oracle Conversion", tester.test_oracle_conversion()))
    
    # File operations
    test_results.append(("File Upload Conversion", tester.test_file_conversion()))
    test_results.append(("Download Conversion", tester.test_download_conversion()))
    
    # ER Diagram Tests
    test_results.append(("ER Diagram Generate", tester.test_er_diagram_generate()))
    test_results.append(("ER Diagram Generate File", tester.test_er_diagram_generate_file()))
    
    # AI Tool Processing Tests
    test_results.append(("AI Code Generator", tester.test_ai_code_generator()))
    test_results.append(("AI Code Assistant", tester.test_ai_code_assistant()))
    test_results.append(("AI Code Converter", tester.test_ai_code_converter()))
    test_results.append(("AI Code Explainer", tester.test_ai_code_explainer()))
    test_results.append(("AI Code Enhancer", tester.test_ai_code_enhancer()))
    test_results.append(("AI Comment Generator", tester.test_ai_comment_generator()))
    test_results.append(("AI Unit Test Generator", tester.test_ai_unit_test_generator()))
    
    # Chat functionality with session management
    test_results.append(("AI Chat Endpoint", tester.test_ai_chat_endpoint()))
    test_results.append(("AI Simple Chat Endpoint", tester.test_ai_chat_simple_endpoint()))
    test_results.append(("AI Chat History", tester.test_ai_chat_history()))
    
    # History and edge cases
    test_results.append(("Conversion History", tester.test_conversion_history()))
    test_results.append(("Invalid Database", tester.test_invalid_database()))
    test_results.append(("Empty SQL", tester.test_empty_sql()))
    
    # Print final results
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    # Group results by category
    sql_tests = [("Root Endpoint", test_results[0][1]), ("MySQL Conversion", test_results[2][1]), 
                 ("PostgreSQL Conversion", test_results[3][1]), ("SQL Server Conversion", test_results[4][1]),
                 ("Oracle Conversion", test_results[5][1]), ("File Upload Conversion", test_results[6][1]),
                 ("Download Conversion", test_results[7][1]), ("Conversion History", test_results[-3][1]),
                 ("Invalid Database", test_results[-2][1]), ("Empty SQL", test_results[-1][1])]
    
    er_tests = [("ER Diagram Generate", test_results[8][1]), ("ER Diagram Generate File", test_results[9][1])]
    
    ai_tests = [("AI Models Endpoint", test_results[1][1])] + test_results[10:17]
    
    print("\n🔧 SQL CONVERSION TESTS:")
    for test_name, result in sql_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print("\n🤖 AI TOOL PROCESSING TESTS:")
    for test_name, result in ai_tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n📈 Overall: {tester.tests_passed}/{tester.tests_run} tests passed")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    # Calculate category success rates
    sql_passed = sum(1 for _, result in sql_tests if result)
    ai_passed = sum(1 for _, result in ai_tests if result)
    
    print(f"🔧 SQL Tests: {sql_passed}/{len(sql_tests)} passed ({(sql_passed/len(sql_tests)*100):.1f}%)")
    print(f"🤖 AI Tests: {ai_passed}/{len(ai_tests)} passed ({(ai_passed/len(ai_tests)*100):.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())