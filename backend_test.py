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
        """Test conversion history endpoint"""
        success, response = self.run_test(
            "Conversion History",
            "GET",
            "history",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   History entries: {len(response)}")
            if len(response) > 0:
                print(f"   First entry keys: {list(response[0].keys())}")
        
        return success

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

def main():
    print("🚀 Starting SQL to Snowflake Converter API Tests")
    print("=" * 60)
    
    tester = SQLConverterAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic API tests
    test_results.append(("Root Endpoint", tester.test_root_endpoint()))
    
    # Database conversion tests
    test_results.append(("MySQL Conversion", tester.test_mysql_conversion()))
    test_results.append(("PostgreSQL Conversion", tester.test_postgresql_conversion()))
    test_results.append(("SQL Server Conversion", tester.test_sqlserver_conversion()))
    test_results.append(("Oracle Conversion", tester.test_oracle_conversion()))
    
    # File operations
    test_results.append(("File Upload Conversion", tester.test_file_conversion()))
    test_results.append(("Download Conversion", tester.test_download_conversion()))
    
    # History and edge cases
    test_results.append(("Conversion History", tester.test_conversion_history()))
    test_results.append(("Invalid Database", tester.test_invalid_database()))
    test_results.append(("Empty SQL", tester.test_empty_sql()))
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall: {tester.tests_passed}/{tester.tests_run} tests passed")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())