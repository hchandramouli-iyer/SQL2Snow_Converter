import React, { useState, useCallback, useRef, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data';
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
import { Popover, PopoverContent, PopoverTrigger } from './components/ui/popover';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from './components/ui/command';
import { 
  Download, Upload, FileText, Database, ArrowRight, Code2, RefreshCw, 
  Settings, ChevronDown, Wand2, Bot, MessageCircle, TestTube, 
  FileCode, Lightbulb, MessageSquare, Cpu, Brain, Network as NetworkIcon, Copy,
  Check, ChevronsUpDown
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

// ER Diagram Visualization Component
const ERDiagramVisualization = ({ diagramData }) => {
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!diagramData || !containerRef.current) return;

    // Prepare nodes (tables)
    const nodes = new DataSet(
      diagramData.tables.map(table => ({
        id: table.name,
        label: createTableLabel(table),
        shape: 'box',
        color: {
          background: '#ffffff',
          border: '#2563eb',
          highlight: {
            background: '#eff6ff',
            border: '#1d4ed8'
          }
        },
        font: {
          face: 'monospace',
          size: 12,
          align: 'left'
        },
        margin: 10,
        widthConstraint: { minimum: 200, maximum: 300 },
        x: table.x || undefined,
        y: table.y || undefined
      }))
    );

    // Prepare edges (relationships)
    const edges = new DataSet(
      diagramData.relationships.map((rel, index) => ({
        id: index,
        from: rel.from_table,
        to: rel.to_table,
        label: `${rel.from_column} → ${rel.to_column}`,
        arrows: 'to',
        color: {
          color: '#6b7280',
          highlight: '#374151'
        },
        font: {
          size: 10,
          color: '#4b5563'
        },
        smooth: {
          type: 'continuous'
        }
      }))
    );

    // Network options
    const options = {
      layout: {
        improvedLayout: true,
        randomSeed: 2
      },
      physics: {
        enabled: true,
        stabilization: {
          enabled: true,
          iterations: 200
        },
        barnesHut: {
          gravitationalConstant: -2000,
          centralGravity: 0.3,
          springLength: 200,
          springConstant: 0.04
        }
      },
      nodes: {
        borderWidth: 2,
        shadow: true,
        chosen: true
      },
      edges: {
        width: 2,
        shadow: true,
        smooth: true
      },
      interaction: {
        dragNodes: true,
        dragView: true,
        zoomView: true,
        selectConnectedEdges: true,
        hover: true
      }
    };

    // Create network
    networkRef.current = new Network(containerRef.current, { nodes, edges }, options);

    // Add click event listener
    networkRef.current.on('click', (event) => {
      if (event.nodes.length > 0) {
        const nodeId = event.nodes[0];
        const table = diagramData.tables.find(t => t.name === nodeId);
        if (table) {
          showTableDetails(table);
        }
      }
    });

    // Cleanup
    return () => {
      if (networkRef.current) {
        networkRef.current.destroy();
        networkRef.current = null;
      }
    };
  }, [diagramData]);

  const createTableLabel = (table) => {
    let label = `📊 ${table.name}\n${'─'.repeat(Math.max(20, table.name.length + 4))}\n`;
    
    table.columns.forEach(column => {
      let icon = '📄';
      if (column.is_primary_key) icon = '🔑';
      else if (column.is_foreign_key) icon = '🔗';
      
      const nullable = column.is_nullable ? '' : ' NOT NULL';
      label += `${icon} ${column.name}: ${column.data_type}${nullable}\n`;
    });

    return label;
  };

  const showTableDetails = (table) => {
    const details = `
Table: ${table.name}
Columns: ${table.columns.length}

Column Details:
${table.columns.map(col => 
  `• ${col.name} (${col.data_type})${col.is_primary_key ? ' [PK]' : ''}${col.is_foreign_key ? ' [FK]' : ''}${!col.is_nullable ? ' [NOT NULL]' : ''}`
).join('\n')}
    `;
    
    alert(details.trim());
  };

  const exportDiagram = (format) => {
    if (!networkRef.current) return;

    if (format === 'png') {
      const canvas = networkRef.current.canvas.getContext().canvas;
      const link = document.createElement('a');
      link.download = 'er-diagram.png';
      link.href = canvas.toDataURL();
      link.click();
    } else if (format === 'svg') {
      // For SVG export, we'd need additional libraries
      alert('SVG export requires additional setup. PNG export is available.');
    }
  };

  return (
    <div className="er-diagram-wrapper">
      <div className="er-diagram-controls mb-4">
        <div className="flex gap-2">
          <Button onClick={() => exportDiagram('png')} className="btn-secondary">
            <Download className="h-4 w-4" />
            Export PNG
          </Button>
          <Button onClick={() => networkRef.current?.fit()} className="btn-secondary">
            Fit to View
          </Button>
          <Button onClick={() => networkRef.current?.redraw()} className="btn-secondary">
            Refresh
          </Button>
        </div>
      </div>
      <div 
        ref={containerRef} 
        className="er-diagram-canvas"
        style={{ 
          width: '100%', 
          height: '600px', 
          border: '1px solid #e5e7eb',
          borderRadius: '8px',
          background: '#fafafa'
        }}
      />
      <div className="er-diagram-legend mt-4">
        <div className="text-sm text-gray-600">
          <div className="grid grid-3 gap-4">
            <div className="flex items-center gap-2">
              <span>🔑</span>
              <span>Primary Key</span>
            </div>
            <div className="flex items-center gap-2">
              <span>🔗</span>
              <span>Foreign Key</span>
            </div>
            <div className="flex items-center gap-2">
              <span>📄</span>
              <span>Regular Column</span>
            </div>
          </div>
          <p className="mt-2 text-xs">
            💡 Click on tables for detailed information. Use mouse to zoom and pan around the diagram.
          </p>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [activeMode, setActiveMode] = useState(AI_TOOLS.SQL_CONVERTER);
  const [activeSection, setActiveSection] = useState('sql-database');
  
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
  
  // History states for database and schema names
  const [sourceDatabaseHistory, setSourceDatabaseHistory] = useState([]);
  const [sourceSchemaHistory, setSourceSchemaHistory] = useState([]);
  const [targetDatabaseHistory, setTargetDatabaseHistory] = useState([]);
  const [targetSchemaHistory, setTargetSchemaHistory] = useState([]);
  
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

  // Tool Categories for Sidebar
  const toolCategories = {
    'sql-database': {
      title: 'SQL & Database',
      icon: <Database className="h-5 w-5" />,
      tools: [
        { key: AI_TOOLS.SQL_CONVERTER, title: 'SQL Converter', icon: <Database className="h-4 w-4" /> },
        { key: AI_TOOLS.ER_DIAGRAM, title: 'ER Diagram', icon: <NetworkIcon className="h-4 w-4" /> }
      ]
    },
    'code-generation': {
      title: 'Code Generation',
      icon: <Wand2 className="h-5 w-5" />,
      tools: [
        { key: AI_TOOLS.CODE_GENERATOR, title: 'Code Generator', icon: <Wand2 className="h-4 w-4" /> },
        { key: AI_TOOLS.CODE_ASSISTANT, title: 'Code Assistant', icon: <Bot className="h-4 w-4" /> }
      ]
    },
    'code-analysis': {
      title: 'Code Analysis',
      icon: <FileCode className="h-5 w-5" />,
      tools: [
        { key: AI_TOOLS.CODE_EXPLAINER, title: 'Code Explainer', icon: <FileCode className="h-4 w-4" /> },
        { key: AI_TOOLS.CODE_ENHANCER, title: 'Code Enhancer', icon: <Lightbulb className="h-4 w-4" /> },
        { key: AI_TOOLS.CODE_CONVERTER, title: 'Language Converter', icon: <ArrowRight className="h-4 w-4" /> }
      ]
    },
    'documentation': {
      title: 'Documentation',
      icon: <MessageSquare className="h-5 w-5" />,
      tools: [
        { key: AI_TOOLS.COMMENT_GENERATOR, title: 'Doc Generator', icon: <MessageSquare className="h-4 w-4" /> },
        { key: AI_TOOLS.UNIT_TEST_GENERATOR, title: 'Test Generator', icon: <TestTube className="h-4 w-4" /> }
      ]
    },
    'ai-assistant': {
      title: 'AI Assistant',
      icon: <MessageCircle className="h-5 w-5" />,
      tools: [
        { key: AI_TOOLS.CHAT, title: 'AI Chat', icon: <MessageCircle className="h-4 w-4" /> }
      ]
    }
  };

  // ComboBox component for database/schema names with history
  const DatabaseComboBox = ({ value, onValueChange, placeholder, history, className }) => {
    const [open, setOpen] = useState(false);
    
    return (
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className={`justify-between ${className}`}
          >
            {value || placeholder}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[300px] p-0">
          <Command>
            <CommandInput 
              placeholder={`Search or type ${placeholder.toLowerCase()}...`}
              value={value}
              onValueChange={onValueChange}
            />
            <CommandEmpty>
              <div className="p-2">
                <Button
                  variant="ghost"
                  className="w-full text-left"
                  onClick={() => {
                    onValueChange(value);
                    setOpen(false);
                  }}
                >
                  Use "{value}"
                </Button>
              </div>
            </CommandEmpty>
            {history.length > 0 && (
              <CommandGroup heading="Recently Used">
                {history.map((item, index) => (
                  <CommandItem
                    key={index}
                    onSelect={() => {
                      onValueChange(item);
                      setOpen(false);
                    }}
                  >
                    <Check className={`mr-2 h-4 w-4 ${value === item ? "opacity-100" : "opacity-0"}`} />
                    {item}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </Command>
        </PopoverContent>
      </Popover>
    );
  };

  const { toast } = useToast();

  // Load history from localStorage on component mount
  useEffect(() => {
    try {
      const loadHistory = (key, setHistory) => {
        const saved = localStorage.getItem(key);
        if (saved) {
          setHistory(JSON.parse(saved));
        }
      };
      
      loadHistory('sourceDatabaseHistory', setSourceDatabaseHistory);
      loadHistory('sourceSchemaHistory', setSourceSchemaHistory);
      loadHistory('targetDatabaseHistory', setTargetDatabaseHistory);
      loadHistory('targetSchemaHistory', setTargetSchemaHistory);
    } catch (error) {
      console.error('Error loading database history:', error);
    }
  }, []);

  // Function to add value to history and update localStorage
  const addToHistory = (value, history, setHistory, storageKey) => {
    if (!value || !value.trim()) return;
    
    const trimmedValue = value.trim();
    const updatedHistory = [trimmedValue, ...history.filter(item => item !== trimmedValue)].slice(0, 10); // Keep last 10 entries
    
    setHistory(updatedHistory);
    localStorage.setItem(storageKey, JSON.stringify(updatedHistory));
  };

  // Handlers for database/schema input changes
  const handleSourceDatabaseNameChange = (value) => {
    setSourceDatabaseName(value);
    if (value && value.trim()) {
      addToHistory(value, sourceDatabaseHistory, setSourceDatabaseHistory, 'sourceDatabaseHistory');
    }
  };

  const handleSourceSchemaNameChange = (value) => {
    setSourceSchemaName(value);
    if (value && value.trim()) {
      addToHistory(value, sourceSchemaHistory, setSourceSchemaHistory, 'sourceSchemaHistory');
    }
  };

  const handleTargetDatabaseNameChange = (value) => {
    setTargetDatabaseName(value);
    if (value && value.trim()) {
      addToHistory(value, targetDatabaseHistory, setTargetDatabaseHistory, 'targetDatabaseHistory');
    }
  };

  const handleTargetSchemaNameChange = (value) => {
    setTargetSchemaName(value);
    if (value && value.trim()) {
      addToHistory(value, targetSchemaHistory, setTargetSchemaHistory, 'targetSchemaHistory');
    }
  };

  // Copy to clipboard function
  const copyToClipboard = async (text, successMessage = 'Copied to clipboard!') => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Success",
        description: successMessage,
      });
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      toast({
        title: "Copy Failed",
        description: "Failed to copy to clipboard",
        variant: "destructive"
      });
    }
  };

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

  // ER Diagram Functions
  const handleErDiagramGenerate = async () => {
    if (!erSqlInput.trim()) {
      toast({
        title: "Validation Error",
        description: "Please provide SQL CREATE TABLE statements",
        variant: "destructive"
      });
      return;
    }

    setIsGeneratingDiagram(true);
    try {
      const response = await axios.post(`${API}/er-diagram/generate`, {
        sql_content: erSqlInput,
        database_type: erDatabaseType
      });

      setErDiagramData(response.data);
      
      toast({
        title: "Diagram Generated",
        description: "ER diagram generated successfully",
      });
    } catch (error) {
      console.error('ER diagram generation error:', error);
      toast({
        title: "Generation Failed",
        description: error.response?.data?.detail || "Failed to generate ER diagram",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingDiagram(false);
    }
  };

  const handleErFileUpload = async () => {
    if (!erSelectedFile) {
      toast({
        title: "Validation Error", 
        description: "Please select a SQL file",
        variant: "destructive"
      });
      return;
    }

    setIsGeneratingDiagram(true);
    try {
      const formData = new FormData();
      formData.append('file', erSelectedFile);
      formData.append('database_type', erDatabaseType);

      const response = await axios.post(`${API}/er-diagram/generate-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setErDiagramData(response.data);
      
      toast({
        title: "Diagram Generated",
        description: `ER diagram generated from ${erSelectedFile.name}`,
      });
    } catch (error) {
      console.error('ER diagram file upload error:', error);
      toast({
        title: "Upload Failed",
        description: error.response?.data?.detail || "Failed to process SQL file",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingDiagram(false);
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
    setErSqlInput('');
    setErSelectedFile(null);
    setErDatabaseType('mysql');
    setErDiagramData(null);
  };

  const getToolIcon = (tool) => {
    const icons = {
      [AI_TOOLS.SQL_CONVERTER]: <Database className="h-5 w-5" />,
      [AI_TOOLS.ER_DIAGRAM]: <NetworkIcon className="h-5 w-5" />,
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
            <div className="flex items-center justify-center gap-3 mb-4">
              <Brain className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">CodeCraft AI - AI Development Tools</h1>
            </div>
            <p className="text-base text-gray-600 max-w-2xl mx-auto">
              Code generation, SQL conversion, and intelligent development automation.
            </p>
          </div>
        </div>
      </header>

      {/* Main Layout with Sidebar */}
      <div className="flex bg-gray-50" style={{ minHeight: 'calc(100vh - 200px)' }}>
        {/* Left Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 shadow-sm">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Development Tools</h2>
            
            {/* AI Configuration in Sidebar */}
            <div className="mb-8 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">AI Configuration</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Provider</label>
                  <Select value={llmProvider} onValueChange={setLlmProvider}>
                    <SelectTrigger className="h-8 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="openai">OpenAI (GPT)</SelectItem>
                      <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                      <SelectItem value="gemini">Google (Gemini)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Model</label>
                  <Select value={llmModel} onValueChange={setLlmModel}>
                    <SelectTrigger className="h-8 text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {availableModels[llmProvider]?.map((model) => (
                        <SelectItem key={model} value={model}>{model}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Tool Categories Navigation */}
            <nav className="space-y-2">
              {Object.entries(toolCategories).map(([sectionKey, section]) => (
                <div key={sectionKey} className="space-y-1">
                  <button
                    onClick={() => setActiveSection(sectionKey)}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-lg transition-colors ${
                      activeSection === sectionKey 
                        ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                        : 'hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    {section.icon}
                    <span className="font-medium">{section.title}</span>
                  </button>
                  
                  {activeSection === sectionKey && (
                    <div className="ml-8 space-y-1">
                      {section.tools.map((tool) => (
                        <button
                          key={tool.key}
                          onClick={() => setActiveMode(tool.key)}
                          className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left rounded-md transition-colors ${
                            activeMode === tool.key 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'hover:bg-gray-100 text-gray-600'
                          }`}
                        >
                          {tool.icon}
                          <span>{tool.title}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>

            {/* Reset Button */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <Button 
                variant="outline" 
                onClick={clearAll}
                className="w-full text-sm"
              >
                <RefreshCw className="h-4 w-4" />
                Reset All Fields
              </Button>
            </div>
          </div>
        </aside>

        {/* Right Main Content */}
        <main className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            {/* Current Tool Header */}
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                {getToolIcon(activeMode)}
                <h1 className="text-2xl font-bold text-gray-900">{getToolTitle(activeMode)}</h1>
              </div>
              <p className="text-gray-600">{getToolDescription(activeMode)}</p>
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
                <div className="space-y-6">
                  {/* Source Database Configuration */}
                  <div>
                    <h4 className="text-md font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Database className="h-4 w-4" />
                      Source Database Details
                    </h4>
                    <div className="grid grid-2 gap-4">
                      <div className="form-group">
                        <label className="form-label">Source Database Type *</label>
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
                        <label className="form-label">Source Database Name</label>
                        <Input
                          placeholder="e.g., my_production_db"
                          value={sourceDatabaseName}
                          onChange={(e) => setSourceDatabaseName(e.target.value)}
                          className="form-input"
                        />
                      </div>
                      
                      <div className="form-group">
                        <label className="form-label">Source Schema Name</label>
                        <Input
                          placeholder="e.g., public, dbo, main"
                          value={sourceSchemaName}
                          onChange={(e) => setSourceSchemaName(e.target.value)}
                          className="form-input"
                        />
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
                  </div>

                  {/* Target Database Configuration */}
                  <div className="border-t border-gray-200 pt-6">
                    <h4 className="text-md font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <ArrowRight className="h-4 w-4" />
                      Target Database Details (Snowflake)
                    </h4>
                    <div className="grid grid-2 gap-4">
                      <div className="form-group">
                        <label className="form-label">Target Database Name</label>
                        <Input
                          placeholder="e.g., ANALYTICS_DB"
                          value={targetDatabaseName}
                          onChange={(e) => setTargetDatabaseName(e.target.value)}
                          className="form-input"
                        />
                      </div>
                      
                      <div className="form-group">
                        <label className="form-label">Target Schema Name</label>
                        <Input
                          placeholder="e.g., PUBLIC, STAGING, PROD"
                          value={targetSchemaName}
                          onChange={(e) => setTargetSchemaName(e.target.value)}
                          className="form-input"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Advanced Options */}
                  <div className="border-t border-gray-200 pt-6">
                    <Collapsible open={showAdvancedOptions} onOpenChange={setShowAdvancedOptions}>
                      <CollapsibleTrigger className="flex items-center gap-2 text-md font-semibold text-gray-800 hover:text-blue-600 transition-colors">
                        <Settings className="h-4 w-4" />
                        Advanced Configuration Options
                        <ChevronDown className={`h-4 w-4 transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`} />
                      </CollapsibleTrigger>
                      <CollapsibleContent className="mt-4">
                        <div className="grid grid-2 gap-4">
                          <div className="form-group">
                            <label className="form-label">Custom Instructions</label>
                            <Textarea
                              placeholder="e.g., Preserve original column comments, use specific data types..."
                              value={customInstructions}
                              onChange={(e) => setCustomInstructions(e.target.value)}
                              className="form-textarea"
                              style={{ minHeight: '80px' }}
                            />
                          </div>
                          
                          <div className="space-y-4">
                            <div className="form-group">
                              <div className="flex items-center justify-between">
                                <label className="form-label">Include Comments</label>
                                <Switch
                                  checked={includeComments}
                                  onCheckedChange={setIncludeComments}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">Generate comments for tables and columns</p>
                            </div>
                            
                            <div className="form-group">
                              <div className="flex items-center justify-between">
                                <label className="form-label">Preserve Case</label>
                                <Switch
                                  checked={preserveCase}
                                  onCheckedChange={setPreserveCase}
                                />
                              </div>
                              <p className="text-xs text-gray-500 mt-1">Maintain original case for identifiers</p>
                            </div>
                          </div>
                        </div>
                      </CollapsibleContent>
                    </Collapsible>
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
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="badge badge-secondary">Original ({sourceDatabase?.toUpperCase()})</span>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(sqlInput, 'Original SQL copied to clipboard!')}
                          className="flex items-center gap-2 text-xs"
                        >
                          <Copy className="h-3 w-3" />
                          Copy SQL
                        </Button>
                      </div>
                      <div className="code-container">
                        <pre className="text-sm" data-testid="original-sql">{sqlInput}</pre>
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="badge badge-primary">Converted (Snowflake)</span>
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(convertedSql, 'Converted SQL copied to clipboard!')}
                          className="flex items-center gap-2 text-xs"
                        >
                          <Copy className="h-3 w-3" />
                          Copy SQL
                        </Button>
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
        ) : activeMode === AI_TOOLS.ER_DIAGRAM ? (
          <div className="space-y-6">
            {/* ER Diagram Input */}
            <Card className="professional-card">
              <CardHeader className="card-header-professional">
                <CardTitle className="card-title-professional">
                  <NetworkIcon className="h-5 w-5" />
                  SQL Input Configuration
                </CardTitle>
                <CardDescription className="card-description-professional">
                  Provide CREATE TABLE statements from your SQL database to generate an interactive ER diagram
                </CardDescription>
              </CardHeader>
              <CardContent className="card-content-professional">
                <div className="grid grid-2 gap-6 mb-6">
                  <div className="form-group">
                    <label className="form-label">Database Type</label>
                    <Select value={erDatabaseType} onValueChange={setErDatabaseType}>
                      <SelectTrigger className="form-select">
                        <SelectValue placeholder="Select database type" />
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
                    <label className="form-label">Upload SQL File (Optional)</label>
                    <Input
                      type="file"
                      accept=".sql,.txt"
                      onChange={(e) => setErSelectedFile(e.target.files[0])}
                      className="form-input"
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label className="form-label">SQL CREATE TABLE Statements</label>
                  <Textarea
                    placeholder="Paste your CREATE TABLE statements here...

Example:
CREATE TABLE users (
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
);"
                    value={erSqlInput}
                    onChange={(e) => setErSqlInput(e.target.value)}
                    className="form-textarea"
                    style={{ minHeight: '300px' }}
                  />
                </div>
                
                <div className="flex gap-4 mt-6">
                  <Button 
                    onClick={handleErDiagramGenerate}
                    disabled={isGeneratingDiagram || !erSqlInput.trim()}
                    className="btn-primary"
                  >
                    {isGeneratingDiagram ? (
                      <>
                        <div className="loading-spinner"></div>
                        Generating Diagram...
                      </>
                    ) : (
                      <>
                        <NetworkIcon className="h-5 w-5" />
                        Generate ER Diagram
                      </>
                    )}
                  </Button>
                  
                  {erSelectedFile && (
                    <Button 
                      onClick={handleErFileUpload}
                      disabled={isGeneratingDiagram}
                      className="btn-secondary"
                    >
                      {isGeneratingDiagram ? (
                        <>
                          <div className="loading-spinner"></div>
                          Processing File...
                        </>
                      ) : (
                        <>
                          <Upload className="h-5 w-5" />
                          Process File
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* ER Diagram Visualization */}
            {erDiagramData && (
              <Card className="professional-card animate-fade-in">
                <CardHeader className="card-header-professional">
                  <CardTitle className="card-title-professional text-green-600">
                    <NetworkIcon className="h-5 w-5" />
                    Interactive ER Diagram
                  </CardTitle>
                  <CardDescription className="card-description-professional">
                    Interactive diagram with {erDiagramData.tables?.length || 0} tables and {erDiagramData.relationships?.length || 0} relationships. 
                    Use mouse to zoom, pan, and click on elements for details.
                  </CardDescription>
                </CardHeader>
                <CardContent className="card-content-professional">
                  <div className="er-diagram-container">
                    <ERDiagramVisualization diagramData={erDiagramData} />
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
          </div>
        </main>
      </div>
      
      <Toaster />
    </div>
  );
}

export default App;