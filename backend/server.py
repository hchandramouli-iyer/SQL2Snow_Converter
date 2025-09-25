from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import re
import tempfile
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# AI Tool Types
class AITool:
    SQL_CONVERTER = "sql_converter"
    ER_DIAGRAM = "er_diagram"
    CODE_GENERATOR = "code_generator"
    CODE_ASSISTANT = "code_assistant"
    CODE_CONVERTER = "code_converter"
    CODE_EXPLAINER = "code_explainer"
    CODE_ENHANCER = "code_enhancer"
    COMMENT_GENERATOR = "comment_generator"
    UNIT_TEST_GENERATOR = "unit_test_generator"
    CHAT = "chat"

# Available LLM Models
AVAILABLE_MODELS = {
    "openai": [
        "gpt-5", "gpt-5-mini", "gpt-4o", "gpt-4o-mini", "gpt-4", "o1", "o1-mini"
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-4-sonnet-20250514"
    ],
    "gemini": [
        "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"
    ]
}

# SQL Conversion Models (existing)
class ConversionRequest(BaseModel):
    sql_content: str
    source_database: str
    conversion_type: str = "basic"
    source_database_name: Optional[str] = None
    source_schema_name: Optional[str] = None
    target_database_name: Optional[str] = None
    target_schema_name: Optional[str] = None
    custom_instructions: Optional[str] = None
    include_comments: bool = True
    preserve_case: bool = False

class ConversionResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_sql: str
    converted_sql: str
    source_database: str
    source_database_name: Optional[str] = None
    source_schema_name: Optional[str] = None
    target_database_name: Optional[str] = None
    target_schema_name: Optional[str] = None
    custom_instructions: Optional[str] = None
    warnings: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

# AI Request Models
class AIRequest(BaseModel):
    tool_type: str
    content: str
    language: Optional[str] = None
    target_language: Optional[str] = None
    framework: Optional[str] = None
    requirements: Optional[str] = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_type: str
    original_content: str
    generated_content: str
    language: Optional[str] = None
    target_language: Optional[str] = None
    llm_provider: str
    llm_model: str
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    message: str
    response: str
    llm_provider: str
    llm_model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ER Diagram Models
class ERDiagramRequest(BaseModel):
    sql_content: str
    database_type: str = "mysql"  # mysql, postgresql, sqlserver, oracle

class TableColumn(BaseModel):
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_nullable: bool = True
    foreign_table: Optional[str] = None
    foreign_column: Optional[str] = None

class ERTable(BaseModel):
    name: str
    columns: List[TableColumn]
    x: Optional[float] = None  # Position for diagram
    y: Optional[float] = None

class ERRelationship(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str = "one-to-many"  # one-to-one, one-to-many, many-to-many

class ERDiagramResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tables: List[ERTable]
    relationships: List[ERRelationship]
    database_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# SQL to Snowflake Converter Class (existing functionality)
class SQLToSnowflakeConverter:
    def __init__(self):
        # Data type mappings for different databases
        self.mysql_type_mappings = {
            'INT': 'NUMBER(38,0)',
            'INTEGER': 'NUMBER(38,0)', 
            'BIGINT': 'NUMBER(38,0)',
            'SMALLINT': 'NUMBER(38,0)',
            'TINYINT': 'NUMBER(38,0)',
            'DECIMAL': 'NUMBER',
            'NUMERIC': 'NUMBER',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'FLOAT8',
            'VARCHAR': 'VARCHAR',
            'CHAR': 'CHAR',
            'TEXT': 'VARCHAR(16777216)',
            'LONGTEXT': 'VARCHAR(16777216)',
            'MEDIUMTEXT': 'VARCHAR(16777216)',
            'TINYTEXT': 'VARCHAR(16777216)',
            'DATE': 'DATE',
            'DATETIME': 'TIMESTAMP_NTZ',
            'TIMESTAMP': 'TIMESTAMP_LTZ',
            'TIME': 'TIME',
            'YEAR': 'NUMBER(4,0)',
            'BOOLEAN': 'BOOLEAN',
            'BOOL': 'BOOLEAN',
            'BINARY': 'BINARY',
            'VARBINARY': 'BINARY',
            'BLOB': 'BINARY',
            'LONGBLOB': 'BINARY',
            'MEDIUMBLOB': 'BINARY',
            'TINYBLOB': 'BINARY',
            'JSON': 'VARIANT'
        }
        
        self.postgresql_type_mappings = {
            'INTEGER': 'NUMBER(38,0)',
            'INT': 'NUMBER(38,0)',
            'INT4': 'NUMBER(38,0)',
            'BIGINT': 'NUMBER(38,0)',
            'INT8': 'NUMBER(38,0)',
            'SMALLINT': 'NUMBER(38,0)',
            'INT2': 'NUMBER(38,0)',
            'SERIAL': 'NUMBER(38,0)',
            'BIGSERIAL': 'NUMBER(38,0)',
            'SMALLSERIAL': 'NUMBER(38,0)',
            'DECIMAL': 'NUMBER',
            'NUMERIC': 'NUMBER',
            'REAL': 'FLOAT4',
            'FLOAT4': 'FLOAT4',
            'DOUBLE PRECISION': 'FLOAT8',
            'FLOAT8': 'FLOAT8',
            'VARCHAR': 'VARCHAR',
            'CHARACTER VARYING': 'VARCHAR',
            'CHAR': 'CHAR',
            'CHARACTER': 'CHAR',
            'TEXT': 'VARCHAR(16777216)',
            'DATE': 'DATE',
            'TIMESTAMP': 'TIMESTAMP_NTZ',
            'TIMESTAMPTZ': 'TIMESTAMP_LTZ',
            'TIME': 'TIME',
            'TIMETZ': 'TIME',
            'BOOLEAN': 'BOOLEAN',
            'BOOL': 'BOOLEAN',
            'BYTEA': 'BINARY',
            'JSON': 'VARIANT',
            'JSONB': 'VARIANT',
            'UUID': 'VARCHAR(36)'
        }
        
        self.sqlserver_type_mappings = {
            'INT': 'NUMBER(38,0)',
            'INTEGER': 'NUMBER(38,0)',
            'BIGINT': 'NUMBER(38,0)',
            'SMALLINT': 'NUMBER(38,0)',
            'TINYINT': 'NUMBER(38,0)',
            'DECIMAL': 'NUMBER',
            'NUMERIC': 'NUMBER',
            'FLOAT': 'FLOAT8',
            'REAL': 'FLOAT4',
            'MONEY': 'NUMBER(19,4)',
            'SMALLMONEY': 'NUMBER(10,4)',
            'VARCHAR': 'VARCHAR',
            'NVARCHAR': 'VARCHAR',
            'CHAR': 'CHAR',
            'NCHAR': 'CHAR',
            'TEXT': 'VARCHAR(16777216)',
            'NTEXT': 'VARCHAR(16777216)',
            'DATE': 'DATE',
            'DATETIME': 'TIMESTAMP_NTZ',
            'DATETIME2': 'TIMESTAMP_NTZ',
            'SMALLDATETIME': 'TIMESTAMP_NTZ',
            'TIME': 'TIME',
            'DATETIMEOFFSET': 'TIMESTAMP_LTZ',
            'BIT': 'BOOLEAN',
            'BINARY': 'BINARY',
            'VARBINARY': 'BINARY',
            'IMAGE': 'BINARY',
            'UNIQUEIDENTIFIER': 'VARCHAR(36)',
            'XML': 'VARCHAR(16777216)'
        }
        
        self.oracle_type_mappings = {
            'NUMBER': 'NUMBER',
            'INTEGER': 'NUMBER(38,0)',
            'INT': 'NUMBER(38,0)',
            'SMALLINT': 'NUMBER(38,0)',
            'DECIMAL': 'NUMBER',
            'NUMERIC': 'NUMBER',
            'FLOAT': 'FLOAT8',
            'BINARY_FLOAT': 'FLOAT4',
            'BINARY_DOUBLE': 'FLOAT8',
            'VARCHAR2': 'VARCHAR',
            'NVARCHAR2': 'VARCHAR',
            'CHAR': 'CHAR',
            'NCHAR': 'CHAR',
            'CLOB': 'VARCHAR(16777216)',
            'NCLOB': 'VARCHAR(16777216)',
            'LONG': 'VARCHAR(16777216)',
            'DATE': 'TIMESTAMP_NTZ',
            'TIMESTAMP': 'TIMESTAMP_NTZ',
            'TIMESTAMP WITH TIME ZONE': 'TIMESTAMP_LTZ',
            'TIMESTAMP WITH LOCAL TIME ZONE': 'TIMESTAMP_LTZ',
            'BLOB': 'BINARY',
            'BFILE': 'VARCHAR(16777216)',
            'RAW': 'BINARY',
            'LONG RAW': 'BINARY'
        }

    def get_type_mapping(self, source_db: str):
        mappings = {
            'mysql': self.mysql_type_mappings,
            'postgresql': self.postgresql_type_mappings,
            'sqlserver': self.sqlserver_type_mappings,
            'oracle': self.oracle_type_mappings
        }
        return mappings.get(source_db.lower(), {})

    def convert_data_types(self, sql_content: str, source_db: str):
        type_mapping = self.get_type_mapping(source_db)
        converted_sql = sql_content
        warnings = []

        for old_type, new_type in type_mapping.items():
            pattern = rf'\b{re.escape(old_type)}\b'
            if re.search(pattern, converted_sql, re.IGNORECASE):
                converted_sql = re.sub(pattern, new_type, converted_sql, flags=re.IGNORECASE)

        return converted_sql, warnings

    def convert_mysql_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []
        converted_sql = re.sub(r'\bAUTO_INCREMENT\b', 'AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'`([^`]+)`', r'"\1"', converted_sql)
        converted_sql = re.sub(r'\s+ENGINE\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\s+DEFAULT\s+CHARSET\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\s+COLLATE\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'mysql')
        warnings.extend(type_warnings)
        return converted_sql, warnings

    def convert_postgresql_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []
        converted_sql = re.sub(r'\bSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bBIGSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bSMALLSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bNOW\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bCURRENT_DATE\b', 'CURRENT_DATE', converted_sql, flags=re.IGNORECASE)
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'postgresql')
        warnings.extend(type_warnings)
        return converted_sql, warnings

    def convert_sqlserver_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []
        converted_sql = re.sub(r'\bIDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\[([^\]]+)\]', r'"\1"', converted_sql)
        converted_sql = re.sub(r'\bGETDATE\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bGETUTCDATE\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'sqlserver')
        warnings.extend(type_warnings)
        return converted_sql, warnings

    def convert_oracle_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []
        converted_sql = re.sub(r'\bSYSDATE\b', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bFROM\s+DUAL\b', '', converted_sql, flags=re.IGNORECASE)
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'oracle')
        warnings.extend(type_warnings)
        return converted_sql, warnings

    def convert_sql_to_snowflake(self, sql_content: str, source_database: str, 
                               source_database_name: str = None, source_schema_name: str = None,
                               target_database_name: str = None, target_schema_name: str = None,
                               custom_instructions: str = None, include_comments: bool = True, 
                               preserve_case: bool = False):
        """Main conversion method with enhanced source and target options"""
        warnings = []
        
        if source_schema_name:
            source_pattern = rf'\b{re.escape(source_schema_name)}\.(\w+)\b'
            sql_content = re.sub(source_pattern, r'\1', sql_content, flags=re.IGNORECASE)
            warnings.append(f"Removed source schema qualification: {source_schema_name}")
        
        if source_database_name:
            db_pattern = rf'\b{re.escape(source_database_name)}\.(\w+\.)?(\w+)\b'
            sql_content = re.sub(db_pattern, r'\2', sql_content, flags=re.IGNORECASE)
            warnings.append(f"Removed source database qualification: {source_database_name}")
        
        if source_database.lower() == 'mysql':
            converted_sql, db_warnings = self.convert_mysql_to_snowflake(sql_content)
        elif source_database.lower() == 'postgresql':
            converted_sql, db_warnings = self.convert_postgresql_to_snowflake(sql_content)
        elif source_database.lower() == 'sqlserver':
            converted_sql, db_warnings = self.convert_sqlserver_to_snowflake(sql_content)
        elif source_database.lower() == 'oracle':
            converted_sql, db_warnings = self.convert_oracle_to_snowflake(sql_content)
        else:
            converted_sql = sql_content
            db_warnings = [f"Unsupported source database: {source_database}"]
        
        warnings.extend(db_warnings)

        if target_database_name:
            converted_sql = f"USE DATABASE {target_database_name};\n\n{converted_sql}"
            warnings.append(f"Added USE DATABASE {target_database_name} statement")
        
        if target_schema_name:
            pattern = r'CREATE TABLE\s+(["`]?)(\w+)\1'
            replacement = rf'CREATE TABLE \1{target_schema_name}.\2\1'
            converted_sql = re.sub(pattern, replacement, converted_sql, flags=re.IGNORECASE)
            pattern = r'(FROM|JOIN|INTO|UPDATE|TABLE)\s+(["`]?)(\w+)\2'
            replacement = rf'\1 \2{target_schema_name}.\3\2'
            converted_sql = re.sub(pattern, replacement, converted_sql, flags=re.IGNORECASE)
            warnings.append(f"Added schema qualification: {target_schema_name}")

        if custom_instructions:
            converted_sql = f"-- Custom Instructions: {custom_instructions}\n{converted_sql}"
            instructions_lower = custom_instructions.lower()
            if 'clustering' in instructions_lower:
                warnings.append("Consider adding CLUSTER BY clause for better performance")
            if 'partition' in instructions_lower:
                warnings.append("Consider partitioning large tables by date or other key columns")
            if 'warehouse' in instructions_lower:
                match = re.search(r'warehouse[:\s]+(\w+)', instructions_lower)
                if match:
                    warehouse_name = match.group(1).upper()
                    converted_sql = f"USE WAREHOUSE {warehouse_name};\n{converted_sql}"
                    warnings.append(f"Added USE WAREHOUSE {warehouse_name} statement")

        if not preserve_case:
            converted_sql = re.sub(r'CREATE TABLE\s+"([^"]+)"', 
                                 lambda m: f'CREATE TABLE "{m.group(1).upper()}"', 
                                 converted_sql, flags=re.IGNORECASE)

        converted_sql = re.sub(r';\s*\n\s*(?=CREATE|ALTER|DROP|INSERT|UPDATE|DELETE)', ';\n\n', converted_sql, flags=re.IGNORECASE)
        
        if 'CREATE TABLE' in converted_sql.upper():
            if not target_schema_name:
                warnings.append("Consider specifying a schema name for better organization")
            if 'clustering' not in custom_instructions.lower() if custom_instructions else True:
                warnings.append("Consider adding clustering keys for large tables in Snowflake")
        
        return converted_sql.strip(), warnings

# ER Diagram Parser Class
class ERDiagramParser:
    def __init__(self):
        pass
    
    def parse_sql_to_er(self, sql_content: str, database_type: str) -> ERDiagramResponse:
        """Parse CREATE TABLE statements and generate ER diagram data"""
        tables = []
        relationships = []
        
        # Clean and split SQL statements
        sql_statements = self._split_sql_statements(sql_content)
        
        # Parse each CREATE TABLE statement
        for statement in sql_statements:
            if self._is_create_table_statement(statement):
                table = self._parse_create_table(statement, database_type)
                if table:
                    tables.append(table)
        
        # Extract relationships from foreign keys
        relationships = self._extract_relationships(tables)
        
        # Auto-position tables for better visualization
        tables = self._auto_position_tables(tables)
        
        return ERDiagramResponse(
            tables=tables,
            relationships=relationships,
            database_type=database_type
        )
    
    def _split_sql_statements(self, sql_content: str) -> List[str]:
        """Split SQL content into individual statements"""
        # Remove comments
        sql_content = re.sub(r'--.*?\n', '\n', sql_content)
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # Split by semicolons, but be careful with semicolons inside strings
        statements = []
        current_statement = ""
        in_string = False
        quote_char = None
        
        i = 0
        while i < len(sql_content):
            char = sql_content[i]
            
            if char in ["'", '"'] and not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char and in_string:
                if i + 1 < len(sql_content) and sql_content[i + 1] == quote_char:
                    # Escaped quote
                    current_statement += char + char
                    i += 1
                else:
                    in_string = False
                    quote_char = None
            elif char == ';' and not in_string:
                current_statement += char
                statement = current_statement.strip()
                if statement:
                    statements.append(statement)
                current_statement = ""
                i += 1
                continue
            
            current_statement += char
            i += 1
        
        # Add the last statement if it doesn't end with semicolon
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements
    
    def _is_create_table_statement(self, statement: str) -> bool:
        """Check if statement is a CREATE TABLE statement"""
        return re.search(r'\bCREATE\s+TABLE\b', statement, re.IGNORECASE) is not None
    
    def _parse_create_table(self, statement: str, database_type: str) -> Optional[ERTable]:
        """Parse a CREATE TABLE statement into an ERTable object"""
        try:
            # Extract table name
            table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:`([^`]+)`|([^\s(]+))', statement, re.IGNORECASE)
            if not table_match:
                return None
            
            table_name = table_match.group(1) or table_match.group(2)
            table_name = table_name.strip('`"[]')
            
            # Extract columns section
            columns_match = re.search(r'\((.*)\)', statement, re.DOTALL)
            if not columns_match:
                return None
            
            columns_text = columns_match.group(1)
            columns = self._parse_columns(columns_text, database_type)
            
            return ERTable(name=table_name, columns=columns)
        
        except Exception as e:
            print(f"Error parsing CREATE TABLE statement: {e}")
            return None
    
    def _parse_columns(self, columns_text: str, database_type: str) -> List[TableColumn]:
        """Parse column definitions from CREATE TABLE statement"""
        columns = []
        
        # Split by commas, but be careful with commas inside parentheses
        column_definitions = self._split_column_definitions(columns_text)
        
        primary_keys = set()
        foreign_keys = {}
        
        for col_def in column_definitions:
            col_def = col_def.strip()
            
            # Skip constraint definitions
            if re.match(r'\s*(PRIMARY\s+KEY|FOREIGN\s+KEY|CONSTRAINT|KEY|INDEX|UNIQUE)', col_def, re.IGNORECASE):
                # Extract primary key information
                pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', col_def, re.IGNORECASE)
                if pk_match:
                    pk_columns = [col.strip('`"[] ') for col in pk_match.group(1).split(',')]
                    primary_keys.update(pk_columns)
                
                # Extract foreign key information
                fk_match = re.search(r'FOREIGN\s+KEY\s*\(([^)]+)\)\s*REFERENCES\s+([^\s(]+)\s*\(([^)]+)\)', col_def, re.IGNORECASE)
                if fk_match:
                    local_col = fk_match.group(1).strip('`"[] ')
                    foreign_table = fk_match.group(2).strip('`"[] ')
                    foreign_col = fk_match.group(3).strip('`"[] ')
                    foreign_keys[local_col] = (foreign_table, foreign_col)
                
                continue
            
            # Parse regular column definition
            column = self._parse_single_column(col_def, database_type)
            if column:
                columns.append(column)
        
        # Apply primary key and foreign key information
        for column in columns:
            if column.name in primary_keys:
                column.is_primary_key = True
                column.is_nullable = False
            
            if column.name in foreign_keys:
                column.is_foreign_key = True
                foreign_table, foreign_col = foreign_keys[column.name]
                column.foreign_table = foreign_table
                column.foreign_column = foreign_col
        
        return columns
    
    def _split_column_definitions(self, columns_text: str) -> List[str]:
        """Split column definitions by commas, respecting parentheses"""
        definitions = []
        current_def = ""
        paren_depth = 0
        in_string = False
        quote_char = None
        
        i = 0
        while i < len(columns_text):
            char = columns_text[i]
            
            if char in ["'", '"'] and not in_string:
                in_string = True
                quote_char = char
            elif char == quote_char and in_string:
                if i + 1 < len(columns_text) and columns_text[i + 1] == quote_char:
                    # Escaped quote
                    current_def += char + char
                    i += 1
                else:
                    in_string = False
                    quote_char = None
            elif not in_string:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ',' and paren_depth == 0:
                    definition = current_def.strip()
                    if definition:
                        definitions.append(definition)
                    current_def = ""
                    i += 1
                    continue
            
            current_def += char
            i += 1
        
        # Add the last definition
        if current_def.strip():
            definitions.append(current_def.strip())
        
        return definitions
    
    def _parse_single_column(self, col_def: str, database_type: str) -> Optional[TableColumn]:
        """Parse a single column definition"""
        try:
            # Extract column name and data type
            col_match = re.match(r'(?:`([^`]+)`|([^\s]+))\s+([^\s,]+(?:\([^)]*\))?)', col_def.strip(), re.IGNORECASE)
            if not col_match:
                return None
            
            column_name = col_match.group(1) or col_match.group(2)
            column_name = column_name.strip('`"[]')
            data_type = col_match.group(3)
            
            # Check for constraints
            is_nullable = 'NOT NULL' not in col_def.upper()
            is_primary_key = 'PRIMARY KEY' in col_def.upper()
            
            return TableColumn(
                name=column_name,
                data_type=data_type,
                is_primary_key=is_primary_key,
                is_nullable=is_nullable
            )
        
        except Exception as e:
            print(f"Error parsing column definition: {e}")
            return None
    
    def _extract_relationships(self, tables: List[ERTable]) -> List[ERRelationship]:
        """Extract relationships from foreign key constraints"""
        relationships = []
        
        for table in tables:
            for column in table.columns:
                if column.is_foreign_key and column.foreign_table:
                    relationship = ERRelationship(
                        from_table=table.name,
                        from_column=column.name,
                        to_table=column.foreign_table,
                        to_column=column.foreign_column or column.name,
                        relationship_type="many-to-one"
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _auto_position_tables(self, tables: List[ERTable]) -> List[ERTable]:
        """Auto-position tables in a grid layout"""
        import math
        
        num_tables = len(tables)
        if num_tables == 0:
            return tables
        
        # Calculate grid dimensions
        cols = math.ceil(math.sqrt(num_tables))
        rows = math.ceil(num_tables / cols)
        
        # Position tables
        for i, table in enumerate(tables):
            col = i % cols
            row = i // cols
            
            # Spread tables across the canvas
            table.x = col * 300 + 150  # 300px spacing, 150px offset
            table.y = row * 200 + 100  # 200px spacing, 100px offset
        
        return tables

# AI Assistant Class
class AIAssistant:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    def get_system_message(self, tool_type: str) -> str:
        system_messages = {
            AITool.CODE_GENERATOR: """You are an expert code generator. Generate clean, efficient, and well-documented code based on user requirements. 
            Always include proper error handling, follow best practices, and add helpful comments. Respond with only the code unless specifically asked for explanations.""",
            
            AITool.CODE_ASSISTANT: """You are an expert coding assistant. Help users fix bugs, improve code quality, add features, and solve programming challenges. 
            Provide clear explanations and actionable solutions. Always suggest best practices and optimizations.""",
            
            AITool.CODE_CONVERTER: """You are an expert code converter. Convert code accurately between different programming languages and frameworks while preserving logic and functionality. 
            Explain any significant changes in approach due to language differences. Only return the converted code unless explanations are requested.""",
            
            AITool.CODE_EXPLAINER: """You are an expert code explainer. Analyze code and provide clear, detailed explanations that are easy to understand. 
            Break down complex concepts, explain the purpose of each part, and highlight important patterns or techniques being used.""",
            
            AITool.CODE_ENHANCER: """You are an expert code enhancer. Analyze code and provide intelligent suggestions for improvements including performance optimizations, 
            better design patterns, security enhancements, and code readability improvements. Provide both the enhanced code and explanations for the changes.""",
            
            AITool.COMMENT_GENERATOR: """You are an expert documentation generator. Analyze code and generate comprehensive, clear, and useful comments and documentation. 
            Include function descriptions, parameter explanations, return values, and usage examples where appropriate.""",
            
            AITool.UNIT_TEST_GENERATOR: """You are an expert unit test generator. Analyze code and generate comprehensive unit tests that cover edge cases, 
            normal operations, and error conditions. Use appropriate testing frameworks and follow testing best practices.""",
            
            AITool.CHAT: """You are an expert coding assistant and programming mentor. Help with any coding queries, provide guidance, 
            explain concepts, debug issues, and offer best practices. Be helpful, clear, and supportive in your responses."""
        }
        return system_messages.get(tool_type, system_messages[AITool.CHAT])

    async def process_ai_request(self, request: AIRequest) -> str:
        """Process AI request using the emergentintegrations library"""
        try:
            # Create session ID if not provided
            session_id = request.session_id or str(uuid.uuid4())
            
            # Initialize LLM chat
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.get_system_message(request.tool_type)
            ).with_model(request.llm_provider, request.llm_model)
            
            # Prepare the user message based on tool type
            user_message_text = self.prepare_user_message(request)
            user_message = UserMessage(text=user_message_text)
            
            # Send message and get response
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

    def prepare_user_message(self, request: AIRequest) -> str:
        """Prepare user message based on the tool type"""
        if request.tool_type == AITool.CODE_GENERATOR:
            msg = f"Generate {request.language or 'Python'} code for the following requirements:\n\n{request.content}"
            if request.framework:
                msg += f"\n\nUse {request.framework} framework."
            if request.requirements:
                msg += f"\n\nAdditional requirements: {request.requirements}"
                
        elif request.tool_type == AITool.CODE_ASSISTANT:
            msg = f"Help me with this {request.language or 'code'} issue:\n\n{request.content}"
            if request.requirements:
                msg += f"\n\nSpecific requirements: {request.requirements}"
                
        elif request.tool_type == AITool.CODE_CONVERTER:
            source_lang = request.language or "the source language"
            target_lang = request.target_language or "the target language"
            msg = f"Convert this {source_lang} code to {target_lang}:\n\n{request.content}"
            if request.framework:
                msg += f"\n\nTarget framework: {request.framework}"
                
        elif request.tool_type == AITool.CODE_EXPLAINER:
            msg = f"Explain this {request.language or 'code'} in detail:\n\n{request.content}"
            
        elif request.tool_type == AITool.CODE_ENHANCER:
            msg = f"Enhance and improve this {request.language or 'code'}:\n\n{request.content}"
            if request.requirements:
                msg += f"\n\nFocus on: {request.requirements}"
                
        elif request.tool_type == AITool.COMMENT_GENERATOR:
            msg = f"Generate comprehensive comments and documentation for this {request.language or 'code'}:\n\n{request.content}"
            
        elif request.tool_type == AITool.UNIT_TEST_GENERATOR:
            msg = f"Generate comprehensive unit tests for this {request.language or 'code'}:\n\n{request.content}"
            if request.framework:
                msg += f"\n\nUse {request.framework} testing framework."
                
        elif request.tool_type == AITool.CHAT:
            msg = request.content
            
        else:
            msg = request.content
            
        return msg

# Initialize classes
converter = SQLToSnowflakeConverter()
ai_assistant = AIAssistant()

# SQL Conversion Routes (existing)
@api_router.post("/convert", response_model=ConversionResponse)
async def convert_sql_text(request: ConversionRequest):
    """Convert SQL text from various databases to Snowflake"""
    try:
        converted_sql, warnings = converter.convert_sql_to_snowflake(
            request.sql_content, 
            request.source_database,
            request.source_database_name,
            request.source_schema_name,
            request.target_database_name,
            request.target_schema_name,
            request.custom_instructions,
            request.include_comments,
            request.preserve_case
        )
        
        response = ConversionResponse(
            original_sql=request.sql_content,
            converted_sql=converted_sql,
            source_database=request.source_database,
            source_database_name=request.source_database_name,
            source_schema_name=request.source_schema_name,
            target_database_name=request.target_database_name,
            target_schema_name=request.target_schema_name,
            custom_instructions=request.custom_instructions,
            warnings=warnings
        )
        
        # Save to history
        history_dict = response.dict()
        await db.conversion_history.insert_one(history_dict)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@api_router.post("/convert-file", response_model=ConversionResponse)
async def convert_sql_file(
    file: UploadFile = File(...), 
    source_database: str = Form(...),
    source_database_name: str = Form(None),
    source_schema_name: str = Form(None),
    target_database_name: str = Form(None),
    target_schema_name: str = Form(None),
    custom_instructions: str = Form(None),
    include_comments: bool = Form(True),
    preserve_case: bool = Form(False)
):
    """Convert SQL file from various databases to Snowflake"""
    try:
        # Read file content
        content = await file.read()
        sql_content = content.decode('utf-8')
        
        converted_sql, warnings = converter.convert_sql_to_snowflake(
            sql_content, 
            source_database,
            source_database_name,
            source_schema_name,
            target_database_name,
            target_schema_name,
            custom_instructions,
            include_comments,
            preserve_case
        )
        
        response = ConversionResponse(
            original_sql=sql_content,
            converted_sql=converted_sql,
            source_database=source_database,
            source_database_name=source_database_name,
            source_schema_name=source_schema_name,
            target_database_name=target_database_name,
            target_schema_name=target_schema_name,
            custom_instructions=custom_instructions,
            warnings=warnings
        )
        
        # Save to history
        history_dict = response.dict()
        await db.conversion_history.insert_one(history_dict)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File conversion failed: {str(e)}")

# ER Diagram Routes
@api_router.post("/er-diagram/generate", response_model=ERDiagramResponse)
async def generate_er_diagram(request: ERDiagramRequest):
    """Generate ER diagram from CREATE TABLE statements"""
    try:
        parser = ERDiagramParser()
        diagram_data = parser.parse_sql_to_er(request.sql_content, request.database_type)
        
        # Save to database
        diagram_dict = diagram_data.dict()
        await db.er_diagrams.insert_one(diagram_dict)
        
        return diagram_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ER diagram generation failed: {str(e)}")

@api_router.post("/er-diagram/generate-file", response_model=ERDiagramResponse)
async def generate_er_diagram_from_file(
    file: UploadFile = File(...),
    database_type: str = Form(default="mysql")
):
    """Generate ER diagram from uploaded SQL file"""
    try:
        # Read file content
        content = await file.read()
        sql_content = content.decode('utf-8')
        
        # Generate ER diagram
        parser = ERDiagramParser()
        diagram_data = parser.parse_sql_to_er(sql_content, database_type)
        
        # Save to database
        diagram_dict = diagram_data.dict()
        await db.er_diagrams.insert_one(diagram_dict)
        
        return diagram_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ER diagram generation from file failed: {str(e)}")

# New AI Routes
@api_router.post("/ai/process", response_model=AIResponse)
async def process_ai_request(request: AIRequest):
    """Process AI requests for various coding tools"""
    try:
        generated_content = await ai_assistant.process_ai_request(request)
        
        response = AIResponse(
            tool_type=request.tool_type,
            original_content=request.content,
            generated_content=generated_content,
            language=request.language,
            target_language=request.target_language,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model,
            session_id=request.session_id
        )
        
        # Save to history
        response_dict = response.dict()
        await db.ai_history.insert_one(response_dict)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

@api_router.post("/ai/chat", response_model=ChatMessage)
async def chat_with_ai(request: AIRequest):
    """Chat with AI assistant"""
    try:
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
            
        # Override tool_type for chat regardless of what's sent
        request.tool_type = AITool.CHAT
        generated_content = await ai_assistant.process_ai_request(request)
        
        chat_message = ChatMessage(
            session_id=request.session_id,
            message=request.content,
            response=generated_content,
            llm_provider=request.llm_provider,
            llm_model=request.llm_model
        )
        
        # Save to chat history
        chat_dict = chat_message.dict()
        await db.chat_history.insert_one(chat_dict)
        
        return chat_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Alternative simplified chat endpoint
@api_router.post("/ai/chat-simple")
async def chat_simple(content: str = Form(...), llm_provider: str = Form("openai"), llm_model: str = Form("gpt-4o-mini"), session_id: str = Form(None)):
    """Simplified chat endpoint"""
    try:
        if not session_id:
            session_id = str(uuid.uuid4())
            
        request = AIRequest(
            tool_type=AITool.CHAT,
            content=content,
            llm_provider=llm_provider,
            llm_model=llm_model,
            session_id=session_id
        )
        
        generated_content = await ai_assistant.process_ai_request(request)
        
        chat_message = ChatMessage(
            session_id=session_id,
            message=content,
            response=generated_content,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        # Save to chat history
        chat_dict = chat_message.dict()
        await db.chat_history.insert_one(chat_dict)
        
        return chat_message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@api_router.get("/ai/models")
async def get_available_models():
    """Get available AI models"""
    return {"models": AVAILABLE_MODELS}

@api_router.get("/ai/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        messages = await db.chat_history.find({"session_id": session_id}).sort("created_at", 1).to_list(100)
        return [ChatMessage(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")

# Existing routes
@api_router.get("/download/{conversion_id}")
async def download_converted_sql(conversion_id: str):
    """Download converted SQL as file"""
    try:
        conversion = await db.conversion_history.find_one({"id": conversion_id})
        if not conversion:
            raise HTTPException(status_code=404, detail="Conversion not found")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as temp_file:
            temp_file.write(conversion['converted_sql'])
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='application/sql',
            filename=f"snowflake_converted_{conversion_id[:8]}.sql"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "AI-Powered Coding Assistant & SQL Converter API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()