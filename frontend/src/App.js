import React, { useState, useCallback } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Alert, AlertDescription } from './components/ui/alert';
import { Input } from './components/ui/input';
import { Switch } from './components/ui/switch';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './components/ui/collapsible';
import { 
  Download, Upload, FileText, Database, ArrowRight, Code2, RefreshCw, 
  Settings, ChevronDown, Wand2, Bot, MessageCircle, TestTube, 
  FileCode, Lightbulb, MessageSquare, Cpu, Brain, Network
} from 'lucide-react';
import { useToast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tool Types
const AI_TOOLS = {
  SQL_CONVERTER: "sql_converter",
  ER_DIAGRAM: "er_diagram",
  CODE_GENERATOR: "code_generator", 
  CODE_ASSISTANT: "code_assistant",
  CODE_CONVERTER: "code_converter",
  CODE_EXPLAINER: "code_explainer",
  CODE_ENHANCER: "code_enhancer",
  COMMENT_GENERATOR: "comment_generator",
  UNIT_TEST_GENERATOR: "unit_test_generator",
  CHAT: "chat"
};

function App() {
  const [activeMode, setActiveMode] = useState(AI_TOOLS.SQL_CONVERTER);
  
  // SQL Converter state
  const [sourceDatabase, setSourceDatabase] = useState('');
  const [sqlInput, setSqlInput] = useState('');
  const [convertedSql, setConvertedSql] = useState('');
  const [warnings, setWarnings] = useState([]);
  const [conversionId, setConversionId] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [sourceDatabaseName, setSourceDatabaseName] = useState('');
  const [sourceSchemaName, setSourceSchemaName] = useState('');
  const [targetDatabaseName, setTargetDatabaseName] = useState('');
  const [targetSchemaName, setTargetSchemaName] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [includeComments, setIncludeComments] = useState(true);
  const [preserveCase, setPreserveCase] = useState(false);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  
  // AI Tools state
  const [aiInput, setAiInput] = useState('');
  const [aiOutput, setAiOutput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [language, setLanguage] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('');
  const [framework, setFramework] = useState('none');
  const [requirements, setRequirements] = useState('');
  const [llmProvider, setLlmProvider] = useState('openai');
  const [llmModel, setLlmModel] = useState('gpt-4o-mini');
  const [sessionId, setSessionId] = useState('');
  
  // Chat state
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  
  // ER Diagram state
  const [erSqlInput, setErSqlInput] = useState('');
  const [erSelectedFile, setErSelectedFile] = useState(null);
  const [erDatabaseType, setErDatabaseType] = useState('mysql');
  const [erDiagramData, setErDiagramData] = useState(null);
  const [isGeneratingDiagram, setIsGeneratingDiagram] = useState(false);
  
  // Available models
  const [availableModels, setAvailableModels] = useState({
    openai: ['gpt-4o-mini', 'gpt-4o', 'gpt-5', 'o1-mini'],
    anthropic: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022'],
    gemini: ['gemini-2.0-flash', 'gemini-1.5-pro']
  });

  // Programming languages and frameworks
  const programmingLanguages = [
    'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'C', 'Go', 'Rust',
    'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'HTML', 'CSS',
    'SQL', 'Bash/Shell', 'PowerShell', 'Dart', 'Elixir', 'Haskell', 'Lua', 'Perl'
  ];

  const frameworks = [
    'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'Express.js', 'Node.js',
    'Django', 'Flask', 'FastAPI', 'Spring Boot', 'ASP.NET', 'Laravel', 'Ruby on Rails',
    'React Native', 'Flutter', 'Xamarin', 'Unity', 'TensorFlow', 'PyTorch', 'Pandas',
    'NumPy', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'Material UI', 'Ant Design',
    'Electron', 'Ionic', 'Cordova', 'GraphQL', 'Apollo', 'Redux', 'Vuex', 'MobX'
  ];

  const { toast } = useToast();

  // Sample SQL for different databases
  const sampleSql = {
    mysql: `CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;`,
    postgresql: `CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);`,
    sqlserver: `CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    email NVARCHAR(100) UNIQUE,
    created_at DATETIME2 DEFAULT GETDATE(),
    is_active BIT DEFAULT 1
);`,
    oracle: `CREATE TABLE users (
    id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    username VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) UNIQUE,
    created_at TIMESTAMP DEFAULT SYSDATE,
    is_active NUMBER(1) DEFAULT 1
);`
  };

  React.useEffect(() => {
    // Load available models on component mount
    const loadModels = async () => {
      try {
        const response = await axios.get(`${API}/ai/models`);
        setAvailableModels(response.data.models);
      } catch (error) {
        console.error('Failed to load models:', error);
      }
    };
    loadModels();
  }, []);

  const loadSampleSql = () => {
    if (sourceDatabase && sampleSql[sourceDatabase]) {
      setSqlInput(sampleSql[sourceDatabase]);
    }
  };

  const handleSqlConvert = async () => {
    if (!sqlInput.trim() || !sourceDatabase) {
      toast({
        title: "Validation Error",
        description: "Please provide SQL content and select source database",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/convert`, {
        sql_content: sqlInput,
        source_database: sourceDatabase,
        conversion_type: 'basic',
        source_database_name: sourceDatabaseName || null,
        source_schema_name: sourceSchemaName || null,
        target_database_name: targetDatabaseName || null,
        target_schema_name: targetSchemaName || null,
        custom_instructions: customInstructions || null,
        include_comments: includeComments,
        preserve_case: preserveCase
      });

      setConvertedSql(response.data.converted_sql);
      setWarnings(response.data.warnings || []);
      setConversionId(response.data.id);
      
      toast({
        title: "Conversion Successful",
        description: `SQL converted from ${sourceDatabase.toUpperCase()} to Snowflake`,
      });
    } catch (error) {
      console.error('Conversion error:', error);
      toast({
        title: "Conversion Failed",
        description: error.response?.data?.detail || "Failed to convert SQL",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAiProcess = async () => {
    if (!aiInput.trim()) {
      toast({
        title: "Validation Error",
        description: "Please provide content to process",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/ai/process`, {
        tool_type: activeMode,
        content: aiInput,
        language: language || null,
        target_language: targetLanguage || null,
        framework: framework && framework !== 'none' ? framework : null,
        requirements: requirements || null,
        llm_provider: llmProvider,
        llm_model: llmModel,
        session_id: sessionId || null
      });

      setAiOutput(response.data.generated_content);
      
      toast({
        title: "Processing Complete",
        description: `${getToolTitle(activeMode)} completed successfully`,
      });
    } catch (error) {
      console.error('AI processing error:', error);
      toast({
        title: "Processing Failed",
        description: error.response?.data?.detail || "Failed to process request",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage = chatInput;
    setChatInput('');
    
    // Add user message to chat
    setChatMessages(prev => [...prev, {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    }]);

    setIsProcessing(true);
    try {
      const response = await axios.post(`${API}/ai/chat`, {
        tool_type: 'chat',
        content: userMessage,
        llm_provider: llmProvider,
        llm_model: llmModel,
        session_id: sessionId || undefined
      });

      // Add AI response to chat
      setChatMessages(prev => [...prev, {
        type: 'ai',
        content: response.data.response,
        timestamp: new Date()
      }]);

      // Set session ID if not already set
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      toast({
        title: "Chat Failed", 
        description: error.response?.data?.detail || "Failed to send message",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const clearAll = () => {
    setSqlInput('');
    setConvertedSql('');
    setWarnings([]);
    setConversionId('');
    setSelectedFile(null);
    setSourceDatabaseName('');
    setSourceSchemaName('');
    setTargetDatabaseName('');
    setTargetSchemaName('');
    setCustomInstructions('');
    setIncludeComments(true);
    setPreserveCase(false);
    setAiInput('');
    setAiOutput('');
    setLanguage('');
    setTargetLanguage('');
    setFramework('none');
    setRequirements('');
    setChatMessages([]);
    setChatInput('');
  };

  const getToolIcon = (tool) => {
    const icons = {
      [AI_TOOLS.SQL_CONVERTER]: <Database className="h-5 w-5" />,
      [AI_TOOLS.ER_DIAGRAM]: <Network className="h-5 w-5" />,
      [AI_TOOLS.CODE_GENERATOR]: <Wand2 className="h-5 w-5" />,
      [AI_TOOLS.CODE_ASSISTANT]: <Bot className="h-5 w-5" />,
      [AI_TOOLS.CODE_CONVERTER]: <ArrowRight className="h-5 w-5" />,
      [AI_TOOLS.CODE_EXPLAINER]: <FileCode className="h-5 w-5" />,
      [AI_TOOLS.CODE_ENHANCER]: <Lightbulb className="h-5 w-5" />,
      [AI_TOOLS.COMMENT_GENERATOR]: <MessageSquare className="h-5 w-5" />,
      [AI_TOOLS.UNIT_TEST_GENERATOR]: <TestTube className="h-5 w-5" />,
      [AI_TOOLS.CHAT]: <MessageCircle className="h-5 w-5" />
    };
    return icons[tool];
  };

  const getToolTitle = (tool) => {
    const titles = {
      [AI_TOOLS.SQL_CONVERTER]: "SQL to Snowflake Converter",
      [AI_TOOLS.ER_DIAGRAM]: "ER Diagram Generator",
      [AI_TOOLS.CODE_GENERATOR]: "AI Code Generator",
      [AI_TOOLS.CODE_ASSISTANT]: "Code Assistant & Debugger", 
      [AI_TOOLS.CODE_CONVERTER]: "Language Converter",
      [AI_TOOLS.CODE_EXPLAINER]: "Code Explainer & Analyzer",
      [AI_TOOLS.CODE_ENHANCER]: "Code Optimizer & Enhancer",
      [AI_TOOLS.COMMENT_GENERATOR]: "Documentation Generator",
      [AI_TOOLS.UNIT_TEST_GENERATOR]: "Unit Test Generator",
      [AI_TOOLS.CHAT]: "AI Coding Assistant Chat"
    };
    return titles[tool];
  };

  const getToolShortName = (tool) => {
    const shortNames = {
      [AI_TOOLS.SQL_CONVERTER]: "SQL Converter",
      [AI_TOOLS.ER_DIAGRAM]: "ER Diagram",
      [AI_TOOLS.CODE_GENERATOR]: "Code Generator",
      [AI_TOOLS.CODE_ASSISTANT]: "Code Assistant", 
      [AI_TOOLS.CODE_CONVERTER]: "Language Converter",
      [AI_TOOLS.CODE_EXPLAINER]: "Code Explainer",
      [AI_TOOLS.CODE_ENHANCER]: "Code Enhancer",
      [AI_TOOLS.COMMENT_GENERATOR]: "Doc Generator",
      [AI_TOOLS.UNIT_TEST_GENERATOR]: "Test Generator",
      [AI_TOOLS.CHAT]: "AI Chat"
    };
    return shortNames[tool];
  };

  const getToolDescription = (tool) => {
    const descriptions = {
      [AI_TOOLS.SQL_CONVERTER]: "Transform SQL from MySQL, PostgreSQL, SQL Server, and Oracle to Snowflake-compatible syntax with advanced configuration options",
      [AI_TOOLS.ER_DIAGRAM]: "Generate interactive Entity-Relationship diagrams from CREATE TABLE statements with clickable elements, zoom, pan, and export capabilities",
      [AI_TOOLS.CODE_GENERATOR]: "Generate efficient, clean, and custom code snippets based on your requirements with AI-powered assistance",
      [AI_TOOLS.CODE_ASSISTANT]: "Get instant help fixing bugs, improving code quality, debugging issues, and adding new features to your codebase",
      [AI_TOOLS.CODE_CONVERTER]: "Convert code seamlessly between different programming languages and frameworks while preserving functionality",
      [AI_TOOLS.CODE_EXPLAINER]: "Understand complex code snippets with detailed explanations, learn new concepts, and improve your coding skills",
      [AI_TOOLS.CODE_ENHANCER]: "Receive intelligent suggestions for performance optimization, security improvements, and code quality enhancements",
      [AI_TOOLS.COMMENT_GENERATOR]: "Generate comprehensive comments, documentation, and API references for better code maintainability",
      [AI_TOOLS.UNIT_TEST_GENERATOR]: "Create thorough unit tests with edge cases and error handling to ensure robust, bug-free code",
      [AI_TOOLS.CHAT]: "Interactive AI assistant for real-time coding help, explanations, and programming guidance"
    };
    return descriptions[tool];
  };

  return (
    <div className="min-h-screen">
      {/* Enhanced Floating Geometric Shapes */}
      <div className="floating-shapes">
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
        <div className="floating-shape"></div>
      </div>
      
      {/* Particle System */}
      <div className="particle-system">
        {Array.from({ length: 50 }, (_, i) => (
          <div 
            key={i} 
            className="particle" 
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 12}s`,
              animationDuration: `${12 + Math.random() * 8}s`
            }}
          />
        ))}
      </div>
      
      {/* Professional Header */}
      <header className="app-header">
        <div className="container">
          <div className="text-center">
            <div className="brand-section">
              <div className="brand-icon">
                <Brain className="h-6 w-6" />
              </div>
              <div className="brand-text">CodeCraft AI</div>
            </div>
            <h1 className="hero-title">AI-Powered Development Suite</h1>
            <p className="hero-subtitle">
              Professional-grade AI tools for code generation, conversion, enhancement, and SQL transformation. 
              Streamline your development workflow with intelligent automation.
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container" style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
        {/* AI Configuration Panel */}
        <div className="professional-card">
          <div className="card-header-professional">
            <h2 className="card-title-professional">
              <Settings className="h-6 w-6" />
              AI Configuration
            </h2>
            <p className="card-description-professional">
              Configure your AI assistant with preferred provider and model for optimal results
            </p>
          </div>
          <div className="card-content-professional">
            <div className="grid grid-3 gap-6">
              <div className="form-group">
                <label className="form-label">AI Provider</label>
                <Select value={llmProvider} onValueChange={setLlmProvider}>
                  <SelectTrigger className="form-select" data-testid="llm-provider-select">
                    <SelectValue placeholder="Select AI provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="openai">
                      <div className="flex items-center gap-2">
                        <div className="status-dot status-online"></div>
                        OpenAI (GPT)
                      </div>
                    </SelectItem>
                    <SelectItem value="anthropic">
                      <div className="flex items-center gap-2">
                        <div className="status-dot status-online"></div>
                        Anthropic (Claude)
                      </div>
                    </SelectItem>
                    <SelectItem value="gemini">
                      <div className="flex items-center gap-2">
                        <div className="status-dot status-online"></div>
                        Google (Gemini)
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Model Version</label>
                <Select value={llmModel} onValueChange={setLlmModel}>
                  <SelectTrigger className="form-select" data-testid="llm-model-select">
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels[llmProvider]?.map((model) => (
                      <SelectItem key={model} value={model}>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm">{model}</span>
                          {model.includes('gpt-5') || model.includes('claude-4') || model.includes('2.0') ? (
                            <span className="badge badge-primary text-xs">Latest</span>
                          ) : null}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="form-group">
                <label className="form-label">Actions</label>
                <Button 
                  variant="outline" 
                  onClick={clearAll}
                  className="btn-secondary w-full"
                  data-testid="clear-all-btn"
                >
                  <RefreshCw className="h-4 w-4" />
                  Reset All Fields
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Tool Selection */}
        <div className="professional-card">
          <div className="card-header-professional">
            <h2 className="card-title-professional">
              <Cpu className="h-6 w-6" />
              Development Tools
            </h2>
            <p className="card-description-professional">
              Select from our comprehensive suite of AI-powered development tools
            </p>
          </div>
          <div className="card-content-professional">
            <div className="tool-grid">
              {Object.values(AI_TOOLS).map((tool) => (
                <div
                  key={tool}
                  className={`tool-card ${activeMode === tool ? 'active' : ''}`}
                  onClick={() => setActiveMode(tool)}
                  data-testid={`tool-${tool}`}
                >
                  <div className="tool-icon">
                    {getToolIcon(tool)}
                  </div>
                  <div className="tool-name">
                    {getToolShortName(tool)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Current Tool Information */}
        <div className="alert alert-info animate-fade-in">
          <div className="flex items-center gap-2">
            {getToolIcon(activeMode)}
            <div className="status-dot status-processing"></div>
          </div>
          <div>
            <div className="font-semibold">{getToolTitle(activeMode)}</div>
            <div className="text-sm opacity-90">{getToolDescription(activeMode)}</div>
          </div>
        </div>

        {/* Tool-specific Content */}
        {activeMode === AI_TOOLS.SQL_CONVERTER ? (
          <div className="space-y-6">
            {/* SQL Converter Controls */}
            <Card className="professional-card">
              <CardHeader className="card-header-professional">
                <CardTitle className="card-title-professional">
                  <Code2 className="h-5 w-5" />
                  Database Configuration
                </CardTitle>
                <CardDescription className="card-description-professional">
                  Configure source database settings and conversion parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="card-content-professional">
                <div className="grid grid-2 gap-6">
                  <div className="form-group">
                    <label className="form-label">Source Database Type</label>
                    <Select value={sourceDatabase} onValueChange={setSourceDatabase}>
                      <SelectTrigger className="form-select" data-testid="source-database-select">
                        <SelectValue placeholder="Choose database type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mysql">MySQL</SelectItem>
                        <SelectItem value="postgresql">PostgreSQL</SelectItem>
                        <SelectItem value="sqlserver">SQL Server</SelectItem>
                        <SelectItem value="oracle">Oracle</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="form-group">
                    <Button 
                      variant="outline" 
                      onClick={loadSampleSql}
                      disabled={!sourceDatabase}
                      className="btn-secondary w-full mt-6"
                      data-testid="load-sample-btn"
                    >
                      <FileText className="h-4 w-4" />
                      Load Sample SQL
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* SQL Input */}
            <Card className="professional-card">
              <CardHeader className="card-header-professional">
                <CardTitle className="card-title-professional">
                  <FileCode className="h-5 w-5" />
                  SQL Input
                </CardTitle>
                <CardDescription className="card-description-professional">
                  Paste your SQL code for conversion to Snowflake syntax
                </CardDescription>
              </CardHeader>
              <CardContent className="card-content-professional">
                <Textarea
                  data-testid="sql-input-textarea"
                  placeholder="-- Paste your SQL code here
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP
);"
                  value={sqlInput}
                  onChange={(e) => setSqlInput(e.target.value)}
                  className="form-textarea"
                  style={{ minHeight: '250px' }}
                />
                
                <div className="text-center mt-6">
                  <Button 
                    onClick={handleSqlConvert}
                    disabled={isProcessing || !sqlInput.trim() || !sourceDatabase}
                    className="btn-primary"
                    data-testid="convert-btn"
                  >
                    {isProcessing ? (
                      <>
                        <div className="loading-spinner"></div>
                        Converting SQL...
                      </>
                    ) : (
                      <>
                        <ArrowRight className="h-5 w-5" />
                        Convert to Snowflake
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* SQL Results */}
            {convertedSql && (
              <Card className="professional-card animate-fade-in">
                <CardHeader className="card-header-professional">
                  <CardTitle className="card-title-professional text-green-600">
                    <ArrowRight className="h-5 w-5" />
                    Conversion Complete
                  </CardTitle>
                  <CardDescription className="card-description-professional">
                    Successfully converted {sourceDatabase?.toUpperCase()} to Snowflake syntax
                  </CardDescription>
                </CardHeader>
                <CardContent className="card-content-professional">
                  <div className="grid grid-2 gap-6">
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="badge badge-secondary">Original ({sourceDatabase?.toUpperCase()})</span>
                      </div>
                      <div className="code-container">
                        <pre className="text-sm" data-testid="original-sql">{sqlInput}</pre>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="badge badge-primary">Converted (Snowflake)</span>
                      </div>
                      <div className="code-container">
                        <pre className="text-sm" data-testid="converted-sql">{convertedSql}</pre>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        ) : activeMode === AI_TOOLS.CHAT ? (
          <Card className="professional-card">
            <CardHeader className="card-header-professional">
              <CardTitle className="card-title-professional">
                <MessageCircle className="h-5 w-5" />
                AI Coding Assistant
              </CardTitle>
              <CardDescription className="card-description-professional">
                Interactive chat with AI for real-time coding help and guidance
              </CardDescription>
            </CardHeader>
            <CardContent className="card-content-professional">
              <div className="chat-container">
                <div className="chat-messages">
                  {chatMessages.length === 0 ? (
                    <div className="text-center text-gray-500 flex flex-col items-center justify-center h-full">
                      <MessageCircle className="h-12 w-12 mb-4 opacity-50" />
                      <p className="text-lg font-medium mb-2">Start a conversation</p>
                      <p className="text-sm">Ask questions about coding, debugging, or development best practices</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {chatMessages.map((msg, index) => (
                        <div key={index} className={`chat-message ${msg.type}`}>
                          <pre className="whitespace-pre-wrap text-sm">{msg.content}</pre>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="chat-input-container">
                  <Textarea
                    placeholder="Ask anything about coding, debugging, or development..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleChat();
                      }
                    }}
                    className="form-textarea"
                    rows={2}
                  />
                  <Button 
                    onClick={handleChat}
                    disabled={isProcessing || !chatInput.trim()}
                    className="btn-primary"
                  >
                    {isProcessing ? (
                      <div className="loading-spinner"></div>
                    ) : (
                      <ArrowRight className="h-5 w-5" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* AI Tool Configuration */}
            <Card className="professional-card">
              <CardHeader className="card-header-professional">
                <CardTitle className="card-title-professional">
                  {getToolIcon(activeMode)}
                  {getToolTitle(activeMode)} Configuration
                </CardTitle>
                <CardDescription className="card-description-professional">
                  Configure language, framework, and specific requirements for optimal AI assistance
                </CardDescription>
              </CardHeader>
              <CardContent className="card-content-professional">
                <div className="grid grid-3 gap-6">
                  {/* Language Selection */}
                  {(activeMode === AI_TOOLS.CODE_GENERATOR || 
                    activeMode === AI_TOOLS.CODE_ASSISTANT ||
                    activeMode === AI_TOOLS.CODE_EXPLAINER ||
                    activeMode === AI_TOOLS.CODE_ENHANCER ||
                    activeMode === AI_TOOLS.COMMENT_GENERATOR ||
                    activeMode === AI_TOOLS.UNIT_TEST_GENERATOR ||
                    activeMode === AI_TOOLS.CODE_CONVERTER) && (
                    <div className="form-group">
                      <label className="form-label">
                        {activeMode === AI_TOOLS.CODE_CONVERTER ? 'Source Language' : 'Programming Language'}
                      </label>
                      <Select value={language} onValueChange={setLanguage}>
                        <SelectTrigger className="form-select" data-testid="language-select">
                          <SelectValue placeholder="Select language" />
                        </SelectTrigger>
                        <SelectContent className="max-h-60">
                          {programmingLanguages.map((lang) => (
                            <SelectItem key={lang} value={lang.toLowerCase()}>{lang}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {/* Target Language for Code Converter */}
                  {activeMode === AI_TOOLS.CODE_CONVERTER && (
                    <div className="form-group">
                      <label className="form-label">Target Language</label>
                      <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                        <SelectTrigger className="form-select" data-testid="target-language-select">
                          <SelectValue placeholder="Select target language" />
                        </SelectTrigger>
                        <SelectContent className="max-h-60">
                          {programmingLanguages.map((lang) => (
                            <SelectItem key={lang} value={lang.toLowerCase()}>{lang}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}

                  {/* Framework Selection */}
                  {(activeMode === AI_TOOLS.CODE_GENERATOR || 
                    activeMode === AI_TOOLS.CODE_ASSISTANT ||
                    activeMode === AI_TOOLS.CODE_CONVERTER ||
                    activeMode === AI_TOOLS.CODE_ENHANCER ||
                    activeMode === AI_TOOLS.UNIT_TEST_GENERATOR) && (
                    <div className="form-group">
                      <label className="form-label">
                        Framework/Library <span className="text-gray-400">(Optional)</span>
                      </label>
                      <Select value={framework} onValueChange={setFramework}>
                        <SelectTrigger className="form-select" data-testid="framework-select">
                          <SelectValue placeholder="Select framework" />
                        </SelectTrigger>
                        <SelectContent className="max-h-60">
                          <SelectItem value="none">No specific framework</SelectItem>
                          {frameworks.map((fw) => (
                            <SelectItem key={fw} value={fw.toLowerCase()}>{fw}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>

                {/* Requirements */}
                <div className="form-group">
                  <label className="form-label">
                    {activeMode === AI_TOOLS.CODE_GENERATOR ? 'Additional Requirements' : 
                     activeMode === AI_TOOLS.CODE_ASSISTANT ? 'Specific Focus Areas' :
                     activeMode === AI_TOOLS.CODE_ENHANCER ? 'Enhancement Priorities' :
                     activeMode === AI_TOOLS.UNIT_TEST_GENERATOR ? 'Testing Requirements' :
                     'Special Instructions'} <span className="text-gray-400">(Optional)</span>
                  </label>
                  <Input
                    placeholder={
                      activeMode === AI_TOOLS.CODE_GENERATOR ? "e.g., Add error handling, use async/await, include logging" :
                      activeMode === AI_TOOLS.CODE_ASSISTANT ? "e.g., Focus on performance, security issues, code clarity" :
                      activeMode === AI_TOOLS.CODE_ENHANCER ? "e.g., Performance, readability, security, maintainability" :
                      activeMode === AI_TOOLS.UNIT_TEST_GENERATOR ? "e.g., Include edge cases, mock external APIs, 100% coverage" :
                      activeMode === AI_TOOLS.CODE_CONVERTER ? "e.g., Preserve comments, optimize for target platform" :
                      "e.g., Specific requirements or focus areas"
                    }
                    value={requirements}
                    onChange={(e) => setRequirements(e.target.value)}
                    className="form-input"
                    data-testid="requirements-input"
                  />
                </div>
              </CardContent>
            </Card>

            {/* AI Input/Output */}
            <Card className="professional-card">
              <CardHeader className="card-header-professional">
                <CardTitle className="card-title-professional">
                  <FileCode className="h-5 w-5" />
                  {activeMode === AI_TOOLS.CODE_GENERATOR ? 'Requirements & Specifications' : 'Code Input'}
                </CardTitle>
                <CardDescription className="card-description-professional">
                  {activeMode === AI_TOOLS.CODE_GENERATOR ? 
                    'Describe what you want to build and the AI will generate the code for you' :
                    'Paste your code for AI analysis and assistance'
                  }
                </CardDescription>
              </CardHeader>
              <CardContent className="card-content-professional">
                <Textarea
                  placeholder={
                    activeMode === AI_TOOLS.CODE_GENERATOR ? 
                      'Example: Create a REST API endpoint that handles user registration with email validation...' :
                      'Paste your code here...'
                  }
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                  className="form-textarea"
                  style={{ minHeight: '300px' }}
                  data-testid="ai-input-textarea"
                />
                
                <div className="text-center mt-6">
                  <Button 
                    onClick={handleAiProcess}
                    disabled={isProcessing || !aiInput.trim()}
                    className="btn-primary"
                    data-testid="process-ai-btn"
                  >
                    {isProcessing ? (
                      <>
                        <div className="loading-spinner"></div>
                        Processing with AI...
                      </>
                    ) : (
                      <>
                        {getToolIcon(activeMode)}
                        <span className="ml-2">Process with AI</span>
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* AI Output */}
            {aiOutput && (
              <Card className="professional-card animate-fade-in">
                <CardHeader className="card-header-professional">
                  <CardTitle className="card-title-professional text-green-600">
                    {getToolIcon(activeMode)}
                    AI Generated Result
                  </CardTitle>
                  <CardDescription className="card-description-professional">
                    Generated content based on your requirements
                  </CardDescription>
                </CardHeader>
                <CardContent className="card-content-professional">
                  <div className="code-container">
                    <pre className="text-sm" data-testid="ai-output">{aiOutput}</pre>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
      
      <Toaster />
    </div>
  );
}

export default App;