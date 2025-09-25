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

# SQL Conversion Models
class ConversionRequest(BaseModel):
    sql_content: str
    source_database: str  # mysql, postgresql, sqlserver, oracle
    conversion_type: str = "basic"  # basic, optimized
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
    target_database_name: Optional[str] = None
    target_schema_name: Optional[str] = None
    custom_instructions: Optional[str] = None
    warnings: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConversionHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_sql: str
    converted_sql: str
    source_database: str
    target_database_name: Optional[str] = None
    target_schema_name: Optional[str] = None
    custom_instructions: Optional[str] = None
    warnings: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

# SQL to Snowflake Converter Class
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
            # Case-insensitive replacement with word boundaries
            pattern = rf'\b{re.escape(old_type)}\b'
            if re.search(pattern, converted_sql, re.IGNORECASE):
                converted_sql = re.sub(pattern, new_type, converted_sql, flags=re.IGNORECASE)

        return converted_sql, warnings

    def convert_mysql_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []

        # Convert AUTO_INCREMENT to Snowflake AUTOINCREMENT
        converted_sql = re.sub(r'\bAUTO_INCREMENT\b', 'AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        
        # Convert backtick quotes to double quotes
        converted_sql = re.sub(r'`([^`]+)`', r'"\1"', converted_sql)
        
        # Convert ENGINE and other MySQL-specific clauses
        converted_sql = re.sub(r'\s+ENGINE\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\s+DEFAULT\s+CHARSET\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\s+COLLATE\s*=\s*\w+', '', converted_sql, flags=re.IGNORECASE)

        # Convert data types
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'mysql')
        warnings.extend(type_warnings)

        return converted_sql, warnings

    def convert_postgresql_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []

        # Convert SERIAL types
        converted_sql = re.sub(r'\bSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bBIGSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bSMALLSERIAL\b', 'NUMBER(38,0) AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)

        # Convert PostgreSQL-specific functions
        converted_sql = re.sub(r'\bNOW\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bCURRENT_DATE\b', 'CURRENT_DATE', converted_sql, flags=re.IGNORECASE)

        # Convert data types
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'postgresql')
        warnings.extend(type_warnings)

        return converted_sql, warnings

    def convert_sqlserver_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []

        # Convert IDENTITY to AUTOINCREMENT
        converted_sql = re.sub(r'\bIDENTITY\s*\(\s*\d+\s*,\s*\d+\s*\)', 'AUTOINCREMENT', converted_sql, flags=re.IGNORECASE)
        
        # Convert square bracket quotes to double quotes
        converted_sql = re.sub(r'\[([^\]]+)\]', r'"\1"', converted_sql)
        
        # Convert GETDATE() and GETUTCDATE()
        converted_sql = re.sub(r'\bGETDATE\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bGETUTCDATE\(\)', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)

        # Convert data types
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'sqlserver')
        warnings.extend(type_warnings)

        return converted_sql, warnings

    def convert_oracle_to_snowflake(self, sql_content: str):
        converted_sql = sql_content
        warnings = []

        # Convert SYSDATE to CURRENT_TIMESTAMP
        converted_sql = re.sub(r'\bSYSDATE\b', 'CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        
        # Convert DUAL table references (common in Oracle)
        converted_sql = re.sub(r'\bFROM\s+DUAL\b', '', converted_sql, flags=re.IGNORECASE)

        # Convert data types
        converted_sql, type_warnings = self.convert_data_types(converted_sql, 'oracle')
        warnings.extend(type_warnings)

        return converted_sql, warnings

    def convert_sql_to_snowflake(self, sql_content: str, source_database: str, 
                               target_database_name: str = None, target_schema_name: str = None,
                               custom_instructions: str = None, include_comments: bool = True, 
                               preserve_case: bool = False):
        """Main conversion method with enhanced options"""
        warnings = []
        
        # Database-specific conversions
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

        # Apply database and schema names
        if target_database_name:
            # Add USE DATABASE statement at the beginning
            converted_sql = f"USE DATABASE {target_database_name};\n\n{converted_sql}"
            warnings.append(f"Added USE DATABASE {target_database_name} statement")
        
        if target_schema_name:
            # Replace table references with schema-qualified names
            # Simple pattern matching for CREATE TABLE statements
            pattern = r'CREATE TABLE\s+(["`]?)(\w+)\1'
            replacement = rf'CREATE TABLE \1{target_schema_name}.\2\1'
            converted_sql = re.sub(pattern, replacement, converted_sql, flags=re.IGNORECASE)
            
            # Handle other statements that might reference tables
            pattern = r'(FROM|JOIN|INTO|UPDATE|TABLE)\s+(["`]?)(\w+)\2'
            replacement = rf'\1 \2{target_schema_name}.\3\2'
            converted_sql = re.sub(pattern, replacement, converted_sql, flags=re.IGNORECASE)
            
            warnings.append(f"Added schema qualification: {target_schema_name}")

        # Apply custom instructions
        if custom_instructions:
            converted_sql = f"-- Custom Instructions: {custom_instructions}\n{converted_sql}"
            
            # Parse and apply some common custom instructions
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

        # Handle case preservation
        if not preserve_case:
            # Convert object names to uppercase (Snowflake default)
            converted_sql = re.sub(r'CREATE TABLE\s+"([^"]+)"', 
                                 lambda m: f'CREATE TABLE "{m.group(1).upper()}"', 
                                 converted_sql, flags=re.IGNORECASE)

        # General Snowflake optimizations and cleanups
        converted_sql = re.sub(r';\s*\n\s*(?=CREATE|ALTER|DROP|INSERT|UPDATE|DELETE)', ';\n\n', converted_sql, flags=re.IGNORECASE)
        
        # Add common Snowflake best practices comment if table creation detected
        if 'CREATE TABLE' in converted_sql.upper():
            if not target_schema_name:
                warnings.append("Consider specifying a schema name for better organization")
            if 'clustering' not in custom_instructions.lower() if custom_instructions else True:
                warnings.append("Consider adding clustering keys for large tables in Snowflake")
        
        return converted_sql.strip(), warnings

# Initialize converter
converter = SQLToSnowflakeConverter()

# API Routes
@api_router.post("/convert", response_model=ConversionResponse)
async def convert_sql_text(request: ConversionRequest):
    """Convert SQL text from various databases to Snowflake"""
    try:
        converted_sql, warnings = converter.convert_sql_to_snowflake(
            request.sql_content, 
            request.source_database,
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

@api_router.get("/download/{conversion_id}")
async def download_converted_sql(conversion_id: str):
    """Download converted SQL as file"""
    try:
        # Find conversion in history
        conversion = await db.conversion_history.find_one({"id": conversion_id})
        if not conversion:
            raise HTTPException(status_code=404, detail="Conversion not found")
        
        # Create temporary file
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

@api_router.get("/history", response_model=List[ConversionHistory])
async def get_conversion_history():
    """Get conversion history"""
    try:
        history = await db.conversion_history.find().sort("created_at", -1).limit(50).to_list(50)
        return [ConversionHistory(**item) for item in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "SQL to Snowflake Converter API"}

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