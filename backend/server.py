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