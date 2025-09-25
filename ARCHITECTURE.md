# CodeCraft AI - Platform Architecture & Implementation Guide

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   UI Framework  │  │  State Management│  │   Visualization │ │
│  │                 │  │                 │  │                 │ │
│  │ • Shadcn UI     │  │ • React Hooks   │  │ • Vis.js Network│ │
│  │ • Tailwind CSS  │  │ • Local State   │  │ • Interactive   │ │
│  │ • Lucide Icons  │  │ • Form Handling │  │   ER Diagrams   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    AI TOOLS SUITE                           │ │
│  │                                                             │ │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │ │SQL Converter│ │ER Diagram   │ │Code Generator│ │AI Chat  │ │ │
│  │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  │                                                             │ │
│  │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │ │Code Assistant│ │Code Converter│ │Code Explainer│ │Enhancer │ │ │
│  │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │ │
│  │                                                             │ │
│  │ ┌─────────────┐ ┌─────────────┐                           │ │
│  │ │Comment Gen  │ │Unit Test Gen│                           │ │
│  │ └─────────────┘ └─────────────┘                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    │ /api/endpoints
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Endpoints │  │  Business Logic │  │   LLM Integration│ │
│  │                 │  │                 │  │                 │ │
│  │ • SQL Convert   │  │ • SQL Parser    │  │ • Emergent Key  │ │
│  │ • ER Diagram    │  │ • ER Parser     │  │ • OpenAI        │ │
│  │ • AI Processing │  │ • AI Assistant  │  │ • Anthropic     │ │
│  │ • Chat Endpoints│  │ • File Handler  │  │ • Gemini        │ │
│  │ • File Upload   │  │ • Validation    │  │ • Multi-Model   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   CORE COMPONENTS                           │ │
│  │                                                             │ │
│  │ ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐ │ │
│  │ │SQLToSnowflake    │  │ERDiagramParser   │  │AIAssistant  │ │ │
│  │ │Converter         │  │                  │  │             │ │ │
│  │ │                  │  │ • Table Parser   │  │ • Tool      │ │ │
│  │ │ • Multi-DB       │  │ • Column Extract │  │   Routing   │ │ │
│  │ │   Support        │  │ • Relationship   │  │ • LLM       │ │ │
│  │ │ • Data Type      │  │   Detection      │  │   Selection │ │ │
│  │ │   Mapping        │  │ • Auto-Position  │  │ • Context   │ │ │
│  │ │ • Syntax Trans   │  │ • Visualization  │  │   Management│ │ │
│  │ └──────────────────┘  └──────────────────┘  └─────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Motor (Async MongoDB Driver)
                                    │ Database Operations
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (MongoDB)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Collections   │  │   Data Models   │  │   Indexing      │ │
│  │                 │  │                 │  │                 │ │
│  │ • conversion    │  │ • Pydantic      │  │ • UUID Primary │ │
│  │   _history      │  │   Models        │  │   Keys          │ │
│  │ • ai_responses  │  │ • JSON          │  │ • Timestamps    │ │
│  │ • chat_messages │  │   Serializable  │  │ • Query Optimization│
│  │ • er_diagrams   │  │ • Type Safety   │  │ • Compound      │ │
│  │ • user_sessions │  │ • Validation    │  │   Indexes       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

### Frontend Technologies
```
React 18.x           - Modern UI framework with hooks
Vite                 - Fast build tool and dev server
Tailwind CSS         - Utility-first CSS framework
Shadcn UI            - Professional component library
Lucide React         - Modern icon library
Vis.js Network       - Interactive network visualization
Axios                - HTTP client for API calls
```

### Backend Technologies
```
FastAPI              - High-performance async web framework
Python 3.9+          - Modern Python runtime
Pydantic             - Data validation and serialization
Motor                - Async MongoDB driver
emergentintegrations - LLM integration library
Python-dotenv        - Environment variable management
```

### Database & Infrastructure
```
MongoDB              - NoSQL document database
Supervisor           - Process management
Docker/Kubernetes    - Containerization platform
Nginx                - Reverse proxy (implicit)
```

## 📁 Project Structure

```
/app/
├── frontend/                    # React Frontend Application
│   ├── public/
│   │   ├── index.html          # Main HTML template
│   │   └── favicon.ico         # Application icon
│   ├── src/
│   │   ├── components/ui/      # Reusable UI Components
│   │   │   ├── button.jsx      # Button component
│   │   │   ├── card.jsx        # Card layouts
│   │   │   ├── select.jsx      # Dropdown selectors
│   │   │   ├── textarea.jsx    # Text input areas
│   │   │   ├── tabs.jsx        # Tab navigation
│   │   │   ├── badge.jsx       # Status badges
│   │   │   ├── alert.jsx       # Notifications
│   │   │   ├── input.jsx       # Input fields
│   │   │   ├── switch.jsx      # Toggle switches
│   │   │   ├── collapsible.jsx # Expandable sections
│   │   │   └── toaster.jsx     # Toast notifications
│   │   ├── hooks/
│   │   │   └── use-toast.js    # Toast notification hook
│   │   ├── App.js              # Main application component
│   │   ├── App.css             # Global styles & animations
│   │   ├── index.js            # Application entry point
│   │   └── index.css           # Base CSS imports
│   ├── package.json            # Dependencies & scripts
│   ├── tailwind.config.js      # Tailwind configuration
│   ├── postcss.config.js       # PostCSS configuration
│   └── .env                    # Environment variables
├── backend/                     # FastAPI Backend Application
│   ├── server.py               # Main FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
├── tests/                      # Test suites
├── scripts/                    # Utility scripts
├── test_result.md             # Testing documentation
└── README.md                  # Project documentation
```

## 🎯 Core Features Implementation

### 1. SQL to Snowflake Converter
**Purpose**: Convert SQL from various databases to Snowflake-compatible syntax

**Implementation Details**:
- **Frontend**: Form with source database selection, SQL input, advanced options
- **Backend**: `SQLToSnowflakeConverter` class with database-specific parsers
- **Supported Databases**: MySQL, PostgreSQL, SQL Server, Oracle
- **Features**: Data type mapping, syntax transformation, comment preservation

**Key Components**:
```python
class SQLToSnowflakeConverter:
    def __init__(self):
        self.data_type_mappings = {...}  # Database-specific mappings
        
    def convert_sql(self, sql_content, source_db, options):
        # Parse and transform SQL syntax
        # Apply data type conversions
        # Handle constraints and indexes
        return converted_sql, warnings
```

### 2. ER Diagram Generator (NEW)
**Purpose**: Generate interactive Entity-Relationship diagrams from CREATE TABLE statements

**Implementation Details**:
- **Frontend**: SQL input, file upload, interactive Vis.js visualization
- **Backend**: `ERDiagramParser` class with SQL parsing logic
- **Supported Features**: Table extraction, relationship detection, auto-positioning

**Key Components**:
```python
class ERDiagramParser:
    def parse_sql_to_er(self, sql_content, database_type):
        # Extract CREATE TABLE statements
        # Parse table structures and columns
        # Identify primary/foreign key relationships
        # Auto-position tables for visualization
        return ERDiagramResponse(tables, relationships)
```

**Frontend Visualization**:
```javascript
const ERDiagramVisualization = ({ diagramData }) => {
    // Vis.js Network integration
    // Interactive table nodes with column details
    // Relationship edges with foreign key indicators
    // Export functionality (PNG, SVG)
    // Zoom, pan, and click interactions
};
```

### 3. AI Development Tools Suite
**Purpose**: Comprehensive AI-powered coding assistance

**Available Tools**:
1. **Code Generator**: Generate code from natural language requirements
2. **Code Assistant**: Debug, fix, and improve existing code
3. **Code Converter**: Transform code between programming languages
4. **Code Explainer**: Provide detailed code explanations
5. **Code Enhancer**: Optimize performance and code quality
6. **Comment Generator**: Generate documentation and comments
7. **Unit Test Generator**: Create comprehensive test suites
8. **AI Chat**: Interactive coding assistant

**Implementation**:
```python
class AIAssistant:
    def process_ai_request(self, request: AIRequest):
        # Route to appropriate tool handler
        # Generate LLM prompts based on tool type
        # Process with selected LLM (OpenAI/Anthropic/Gemini)
        # Return formatted response
        
    def get_system_message(self, tool_type: str):
        # Tool-specific system prompts
        # Context-aware instructions
        # Output formatting guidelines
```

### 4. Multi-LLM Integration
**Purpose**: Support multiple LLM providers with unified interface

**Supported Providers**:
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-5, o1-mini
- **Anthropic**: Claude-3-5-sonnet, Claude-3-5-haiku
- **Gemini**: Gemini-2.0-flash, Gemini-1.5-pro

**Integration**:
```python
# Using emergentintegrations library
from emergentintegrations.llm.chat import LlmChat, UserMessage

class AIAssistant:
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        
    async def generate_response(self, messages, provider, model):
        llm_chat = LlmChat(api_key=self.api_key)
        response = await llm_chat.generate_response(
            messages=messages,
            provider=provider,
            model=model
        )
        return response.content
```

## 🎨 UI/UX Design System

### Visual Design Philosophy
- **Professional**: Clean, modern interface with subtle animations
- **Accessible**: High contrast ratios, keyboard navigation
- **Responsive**: Mobile-first design with desktop enhancements
- **Consistent**: Unified component library and design tokens

### Design System Components

#### Color Palette
```css
:root {
  /* Primary Brand Colors */
  --primary-50: #eff6ff;    /* Light blue backgrounds */
  --primary-500: #3b82f6;   /* Primary brand blue */
  --primary-600: #2563eb;   /* Primary button color */
  --primary-700: #1d4ed8;   /* Darker blue accents */
  
  /* Neutral Grays */
  --gray-50: #f8fafc;       /* Light backgrounds */
  --gray-100: #f1f5f9;      /* Card backgrounds */
  --gray-200: #e2e8f0;      /* Borders */
  --gray-600: #475569;      /* Text secondary */
  --gray-800: #1e293b;      /* Text primary */
  --gray-900: #0f172a;      /* Headings */
}
```

#### Typography System
```css
.hero-title {
  font-size: 3.5rem;        /* 56px */
  font-weight: 900;         /* Black weight */
  line-height: 1.1;         /* Tight spacing */
}

.brand-text {
  font-size: 2.5rem;        /* 40px */
  font-weight: 900;         /* Enhanced visibility */
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
}
```

#### Animation System
```css
/* Floating Shapes Background */
.floating-shape {
  animation: advancedFloat 20s infinite ease-in-out;
  transform-style: preserve-3d;
}

/* Interactive Card Hover Effects */
.professional-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

/* Button Interactions */
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4);
}
```

## 🔄 Data Flow Architecture

### Request/Response Flow
```
1. User Action (Frontend)
   ↓
2. Form Validation & State Update
   ↓
3. HTTP Request to Backend API
   ↓
4. FastAPI Route Handler
   ↓
5. Business Logic Processing
   ↓
6. Database Operations (MongoDB)
   ↓
7. LLM API Calls (if needed)
   ↓
8. Response Formatting
   ↓
9. JSON Response to Frontend
   ↓
10. UI Update & User Feedback
```

### State Management
```javascript
// React Hook-based State Management
const App = () => {
  // Tool Selection State
  const [activeMode, setActiveMode] = useState(AI_TOOLS.SQL_CONVERTER);
  
  // SQL Converter State
  const [sourceDatabase, setSourceDatabase] = useState('');
  const [sqlInput, setSqlInput] = useState('');
  const [convertedSql, setConvertedSql] = useState('');
  
  // ER Diagram State
  const [erSqlInput, setErSqlInput] = useState('');
  const [erDiagramData, setErDiagramData] = useState(null);
  
  // AI Tools State
  const [aiInput, setAiInput] = useState('');
  const [aiOutput, setAiOutput] = useState('');
  const [llmProvider, setLlmProvider] = useState('openai');
  
  // Chat State
  const [chatMessages, setChatMessages] = useState([]);
  
  // Global State
  const [isProcessing, setIsProcessing] = useState(false);
};
```

## 🛡️ Security & Performance

### Security Measures
- **Environment Variables**: Sensitive data stored in .env files
- **API Key Management**: Secure handling of LLM API keys
- **Input Validation**: Pydantic models for request validation
- **CORS Configuration**: Controlled cross-origin access
- **SQL Injection Prevention**: Parameterized queries and input sanitization

### Performance Optimizations
- **Async Operations**: Non-blocking I/O with FastAPI and Motor
- **Connection Pooling**: Efficient database connections
- **Lazy Loading**: Components loaded on demand
- **Caching Strategy**: Browser caching for static assets
- **Code Splitting**: Optimized bundle sizes with Vite

## 📊 Database Schema

### MongoDB Collections

#### `conversion_history`
```json
{
  "_id": "uuid-string",
  "source_database": "mysql",
  "sql_content": "CREATE TABLE...",
  "converted_sql": "CREATE TABLE...",
  "warnings": ["warning1", "warning2"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `er_diagrams`
```json
{
  "_id": "uuid-string",
  "database_type": "mysql",
  "tables": [
    {
      "name": "users",
      "columns": [
        {
          "name": "id",
          "data_type": "INT",
          "is_primary_key": true,
          "is_foreign_key": false,
          "is_nullable": false
        }
      ],
      "x": 150,
      "y": 100
    }
  ],
  "relationships": [
    {
      "from_table": "orders",
      "from_column": "user_id",
      "to_table": "users",
      "to_column": "id",
      "relationship_type": "many-to-one"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `ai_responses`
```json
{
  "_id": "uuid-string",
  "tool_type": "code_generator",
  "original_content": "Create a user authentication system",
  "generated_content": "# User Authentication System...",
  "language": "python",
  "framework": "fastapi",
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "session_id": "session-uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### `chat_messages`
```json
{
  "_id": "uuid-string",
  "session_id": "session-uuid",
  "message": "How do I optimize this SQL query?",
  "response": "Here are several optimization strategies...",
  "llm_provider": "anthropic",
  "llm_model": "claude-3-5-sonnet",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🚀 Deployment Architecture

### Container Configuration
```
┌─────────────────────────────────────────┐
│           Kubernetes Cluster           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Frontend   │  │    Backend      │  │
│  │  Container  │  │   Container     │  │
│  │             │  │                 │  │
│  │ • Port 3000 │  │ • Port 8001     │  │
│  │ • React App │  │ • FastAPI       │  │
│  │ • Nginx     │  │ • Python 3.9+   │  │
│  └─────────────┘  └─────────────────┘  │
│                                         │
│         ┌─────────────────────┐        │
│         │    MongoDB Atlas    │        │
│         │   (External SaaS)   │        │
│         └─────────────────────┘        │
└─────────────────────────────────────────┘
```

### Service Management
```bash
# Supervisor Configuration
sudo supervisorctl status
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
sudo supervisorctl restart all
```

### Environment Configuration
```bash
# Frontend Environment (.env)
REACT_APP_BACKEND_URL=https://api.domain.com

# Backend Environment (.env) 
MONGO_URL=mongodb://mongo:27017/database
EMERGENT_LLM_KEY=emergent_universal_key
DB_NAME=codecraft_ai
```

## 📈 Scalability Considerations

### Horizontal Scaling
- **Stateless Design**: No server-side sessions, enabling easy scaling
- **Load Balancing**: Multiple backend instances behind load balancer
- **Database Sharding**: MongoDB horizontal partitioning for large datasets
- **CDN Integration**: Static asset delivery optimization

### Vertical Optimizations
- **Resource Monitoring**: CPU, memory, and I/O optimization
- **Connection Pooling**: Efficient database connection management
- **Async Processing**: Non-blocking operations throughout stack
- **Caching Layers**: Redis for frequent queries and session data

## 🔍 Monitoring & Observability

### Logging Strategy
```python
# Backend Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
    return response
```

### Error Handling
```python
# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## 🎯 Future Enhancement Opportunities

### Technical Enhancements
1. **Real-time Collaboration**: WebSocket integration for multi-user editing
2. **Advanced Caching**: Redis implementation for improved performance
3. **API Rate Limiting**: Request throttling and quota management
4. **Advanced Analytics**: User behavior tracking and performance metrics
5. **Microservices**: Service decomposition for better scalability

### Feature Expansions
1. **Database Migration Tools**: Schema version control and migration scripts
2. **Visual Query Builder**: Drag-and-drop SQL query construction
3. **Advanced Export Options**: PDF reports, Excel exports, API documentation
4. **Template Library**: Pre-built SQL templates and code snippets
5. **Team Collaboration**: Shared workspaces and project management

This architecture provides a robust, scalable foundation for the CodeCraft AI platform while maintaining clean code organization and professional development practices.