# CodeCraft AI - AI-Powered Development Suite

## 🚀 Overview

CodeCraft AI is a comprehensive AI-powered development platform that provides intelligent tools for SQL conversion, code generation, and database visualization. Built with React, FastAPI, and MongoDB, it offers a suite of 9 AI development tools with modern visual effects and professional UI.

## ✨ Key Features

### 🔧 Core Tools
- **SQL to Snowflake Converter** - Convert SQL from MySQL, PostgreSQL, SQL Server, Oracle to Snowflake
- **Interactive ER Diagram Generator** - Generate visual database schemas with relationships
- **AI Code Generator** - Generate code in multiple programming languages
- **AI Code Assistant** - Get help with coding questions and debugging
- **Code Converter** - Convert code between different programming languages
- **Code Explainer** - Get detailed explanations of code functionality
- **Code Enhancer** - Improve code quality and performance
- **Comment Generator** - Auto-generate meaningful code comments
- **Unit Test Generator** - Create comprehensive unit tests
- **AI Chat Assistant** - Interactive AI assistant for development help

### 🎨 Advanced UI Features
- **Visual Effects** - Particle systems, 3D animations, morphing backgrounds
- **Interactive Elements** - Hover effects, smooth transitions, glassmorphism design
- **Responsive Design** - Works perfectly on desktop and mobile devices
- **Dark Theme Support** - Professional dark theme with gradient accents

### 💾 Data Management
- **Database Configuration** - Support for multiple database types and schemas
- **File Operations** - Upload/download SQL files with conversion history
- **Input History** - Smart history management for database and schema names
- **Session Management** - Persistent chat sessions with conversation history

## 🏗️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn UI** - Modern component library
- **Vis.js Network** - Interactive network visualization for ER diagrams
- **Lucide React** - Beautiful icon library

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database for data persistence
- **Emergent Integrations** - Multi-LLM support (OpenAI, Anthropic, Gemini)
- **Pydantic** - Data validation and serialization
- **Motor** - Async MongoDB driver

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- MongoDB (local or cloud)
- Yarn package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd codecraft-ai
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup** 
```bash
cd frontend
yarn install
```

4. **Environment Configuration**

Create `/backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017/codecraft_ai
EMERGENT_LLM_KEY=your_llm_key_here
```

Create `/frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Development

1. **Start Backend**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

2. **Start Frontend**
```bash
cd frontend
yarn start
```

3. **Access Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

## 📁 Project Structure

```
codecraft-ai/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── App.js           # Main application component
│   │   ├── App.css          # Global styles and animations
│   │   ├── components/      # Reusable UI components
│   │   └── hooks/           # Custom React hooks
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                 # FastAPI backend application
│   ├── server.py           # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Container configuration
├── tests/                  # Test files
│   ├── test_basic.py      # Basic functionality tests
│   └── __init__.py
├── .github/
│   └── workflows/
│       └── deploy.yml     # GitHub Actions deployment
└── README.md             # This file
```

## 🔧 API Endpoints

### SQL Conversion
- `POST /api/convert` - Convert SQL text
- `POST /api/convert-file` - Convert SQL file
- `GET /api/download/{filename}` - Download converted files

### ER Diagram
- `POST /api/er-diagram/generate` - Generate from SQL text
- `POST /api/er-diagram/generate-file` - Generate from SQL file

### AI Tools
- `POST /api/ai/process` - Process AI tool requests
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/chat-simple` - Simple chat interface
- `GET /api/ai/chat-history` - Get chat history
- `GET /api/ai/models` - Get available models

## 🎯 Usage Examples

### SQL Conversion
```javascript
// Convert MySQL to Snowflake
const response = await fetch('/api/convert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sql_text: "CREATE TABLE users (id INT, name VARCHAR(100))",
    source_db: "mysql",
    target_database: "ANALYTICS_DW",
    target_schema: "STAGING"
  })
});
```

### ER Diagram Generation
```javascript
// Generate ER diagram
const response = await fetch('/api/er-diagram/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    sql_text: "CREATE TABLE users...",
    database_type: "mysql"
  })
});
```

### AI Code Generation
```javascript
// Generate code
const response = await fetch('/api/ai/process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool_type: "code_generator",
    prompt: "Create a React component for user login",
    language: "javascript",
    provider: "openai",
    model: "gpt-4"
  })
});
```

## 🚀 Deployment

### GitHub Pages (Frontend Only)

1. **Configure GitHub Pages**
   - Enable GitHub Pages in repository settings
   - Select GitHub Actions as source

2. **Deploy**
   - Push to main branch
   - GitHub Actions will automatically build and deploy

### Full-Stack Deployment

For backend deployment, consider:
- **Vercel** - Frontend + Serverless backend
- **Netlify** - Frontend + Netlify Functions
- **Railway** - Full-stack with database
- **Render** - Full-stack deployment

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests (if configured)
cd frontend
yarn test
```

### Testing Features
- SQL conversion for all database types
- ER diagram generation and visualization
- AI tool functionality across all providers
- File upload/download operations
- Chat system with session management

## 🔐 Environment Variables

### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017/codecraft_ai
EMERGENT_LLM_KEY=your_universal_llm_key
```

### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 📝 Features in Detail

### Visual Effects System
- **Particle Animation** - 50 floating particles with physics
- **Morphing Backgrounds** - Dynamic gradient animations
- **3D Transformations** - Enhanced hover effects and transitions
- **Glassmorphism Design** - Modern glass-like UI elements

### AI Integration
- **Multi-LLM Support** - OpenAI GPT-4, Anthropic Claude, Google Gemini
- **Emergent Universal Key** - Single key for all LLM providers
- **Model Selection** - Choose specific models for different tasks
- **Session Management** - Persistent chat conversations

### Database Support
- **Source Databases** - MySQL, PostgreSQL, SQL Server, Oracle
- **Target Database** - Snowflake with full data type mapping
- **Schema Configuration** - Custom database and schema naming
- **Advanced Options** - Include comments, preserve case settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🎉 Acknowledgments

- Built with modern web technologies
- Powered by advanced AI models
- Designed for developer productivity
- Community-driven development

---

**CodeCraft AI** - Empowering developers with AI-powered tools for modern development workflows.
