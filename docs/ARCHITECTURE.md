# Cold Case Analysis (CoLD) - Architecture and Data Flow Documentation

This document provides a comprehensive overview of the Cold Case Analysis project structure, data flow patterns, and component interactions.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Application Components](#application-components)
- [Data Flow Patterns](#data-flow-patterns)
- [Data Models and Schema](#data-models-and-schema)
- [Component Interactions](#component-interactions)
- [Setup and Configuration](#setup-and-configuration)

## Project Overview

The Cold Case Analysis (CoLD) project is a comprehensive legal analysis system that leverages Large Language Models (LLMs) to analyze court decisions concerning choice of law in international commercial contracts. The system provides three distinct interfaces for different use cases:

1. **CLI Case Analyzer** - Batch processing tool for analyzing multiple court cases
2. **LangGraph Analysis Engine** - Advanced workflow orchestration with human-in-the-loop capabilities  
3. **Streamlit Web Application** - Interactive web interface for guided analysis

## System Architecture

```mermaid
graph TB
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT-4o, GPT-4o-mini]
        Llama[Llama API<br/>llama3.1]
        Airtable[Airtable API<br/>Data Source]
        PostgreSQL[(PostgreSQL<br/>Results Storage)]
    end

    subgraph "Cold Case Analysis System"
        subgraph "CLI Application"
            CLI[CLI Case Analyzer<br/>main.py]
            CaseAnalyzer[CaseAnalyzer Class<br/>Batch Processing]
            DataHandler[Data Handler<br/>Local/Airtable]
            Evaluator[Result Evaluator<br/>Ground Truth Comparison]
        end

        subgraph "LangGraph Engine"
            LangGraph[LangGraph Main<br/>main.py]
            GraphConfig[Graph Configuration<br/>Node Orchestration]
            Nodes[Analysis Nodes<br/>COL, Theme, Facts, etc.]
            Tools[Analysis Tools<br/>LLM Integration]
            Interrupts[Human Interrupts<br/>Validation Points]
        end

        subgraph "Streamlit Web App"
            StreamlitApp[Streamlit App<br/>app.py]
            MainWorkflow[Main Workflow<br/>Step Orchestration]
            Components[UI Components<br/>Input, Processing, Display]
            StateManager[State Manager<br/>Session Management]
            Database[Database Handler<br/>Result Persistence]
        end

        subgraph "Shared Components"
            LLMHandler[LLM Handler<br/>Model Access]
            PromptLibrary[Prompt Library<br/>Analysis Templates]
            ConfigManager[Config Manager<br/>Settings & Secrets]
        end
    end

    subgraph "Data Sources"
        LocalFiles[Local Excel Files<br/>cases.xlsx, concepts.xlsx]
        GroundTruth[Ground Truth Data<br/>Evaluation Reference]
        DemoData[Demo Case Data<br/>BGE 132 III 285]
    end

    %% External API connections
    CLI --> OpenAI
    CLI --> Llama
    CLI --> Airtable
    LangGraph --> OpenAI
    StreamlitApp --> OpenAI
    StreamlitApp --> PostgreSQL

    %% Data source connections
    CLI --> LocalFiles
    CLI --> GroundTruth
    StreamlitApp --> DemoData

    %% Internal component connections
    CLI --> CaseAnalyzer
    CaseAnalyzer --> DataHandler
    CaseAnalyzer --> Evaluator
    
    LangGraph --> GraphConfig
    GraphConfig --> Nodes
    Nodes --> Tools
    Nodes --> Interrupts

    StreamlitApp --> MainWorkflow
    MainWorkflow --> Components
    Components --> StateManager
    Components --> Database

    %% Shared component usage
    CLI --> LLMHandler
    LangGraph --> LLMHandler
    StreamlitApp --> LLMHandler
    
    CLI --> PromptLibrary
    LangGraph --> PromptLibrary
    StreamlitApp --> PromptLibrary

    CLI --> ConfigManager
    LangGraph --> ConfigManager
    StreamlitApp --> ConfigManager

    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef cli fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef langgraph fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef streamlit fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef shared fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef data fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class OpenAI,Llama,Airtable,PostgreSQL external
    class CLI,CaseAnalyzer,DataHandler,Evaluator cli
    class LangGraph,GraphConfig,Nodes,Tools,Interrupts langgraph
    class StreamlitApp,MainWorkflow,Components,StateManager,Database streamlit
    class LLMHandler,PromptLibrary,ConfigManager shared
    class LocalFiles,GroundTruth,DemoData data
```

## Application Components

### 1. CLI Case Analyzer

**Location**: `cold_case_analyzer/`

The CLI application provides a command-line interface for batch processing of court cases with interactive model selection.

#### Key Components:

- **Main Entry Point** (`main.py`): Interactive menu system for data source and model selection
- **CaseAnalyzer Class** (`case_analyzer/__init__.py`): Core analysis logic with sequential processing
- **Data Handlers** (`data_handler/`): Local file and Airtable data retrieval
- **Evaluator** (`evaluator/`): Ground truth comparison and result validation

#### Processing Flow:

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI Main
    participant Analyzer as CaseAnalyzer
    participant LLM as LLM Handler
    participant Data as Data Source

    User->>CLI: Run python main.py
    CLI->>User: Select data source (Own data/Airtable)
    CLI->>User: Select model (gpt-4o/gpt-4o-mini/llama3.1)
    CLI->>Data: Fetch cases and concepts
    
    loop For each case
        CLI->>Analyzer: Create CaseAnalyzer instance
        Analyzer->>LLM: Extract COL section
        Analyzer->>LLM: Get abstract
        Analyzer->>LLM: Get relevant facts  
        Analyzer->>LLM: Get PIL provisions
        Analyzer->>LLM: Get choice of law issue
        Analyzer->>LLM: Get court's position
        Analyzer->>CLI: Return analysis results
    end
    
    CLI->>Data: Save results to CSV
    CLI->>User: Offer evaluation option
    
    alt User chooses evaluation
        CLI->>Evaluator: Compare with ground truth
        Evaluator->>User: Display evaluation metrics
    end
```

### 2. LangGraph Analysis Engine

**Location**: `cold_case_analyzer/cca_langgraph/`

The LangGraph engine provides advanced workflow orchestration with human-in-the-loop capabilities using a graph-based approach.

#### Key Components:

- **Graph Configuration** (`graph_config.py`): Node definitions and workflow orchestration
- **Analysis Nodes** (`nodes/`): Individual processing steps (COL extraction, theme classification, etc.)
- **Analysis Tools** (`tools/`): LLM integration utilities
- **Interrupt Handlers** (`nodes/interrupt_handler.py`): Human validation checkpoints

#### Workflow Architecture:

```mermaid
graph TD
    Start([Court Decision Text])
    
    subgraph "LangGraph Workflow"
        TextInput[Text Input Node]
        COLExtract[COL Section Extraction]
        COLValidation{User COL Validation}
        ThemeClass[PIL Theme Classification]
        ThemeValidation{User Theme Validation}
        
        subgraph "Analysis Phase"
            Abstract[Abstract Extraction]
            Facts[Relevant Facts]
            Provisions[PIL Provisions]
            Issue[COL Issue Identification]
            Position[Court's Position]
        end
        
        Formatter[Result Formatting]
        FinalReview{Final Analysis Review}
        End([Complete Analysis])
    end

    Start --> TextInput
    TextInput --> COLExtract
    COLExtract --> COLValidation
    
    COLValidation -->|Approved| ThemeClass
    COLValidation -->|Rejected| COLExtract
    
    ThemeClass --> ThemeValidation
    ThemeValidation -->|Approved| Abstract
    ThemeValidation -->|Rejected| ThemeClass
    
    Abstract --> Facts
    Facts --> Provisions
    Provisions --> Issue
    Issue --> Position
    Position --> Formatter
    Formatter --> FinalReview
    
    FinalReview -->|Approved| End
    FinalReview -->|Refinement Needed| Formatter

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef decision fill:#fff3e0,stroke:#f57c00
    classDef output fill:#e8f5e8,stroke:#388e3c

    class TextInput,Start input
    class COLExtract,ThemeClass,Abstract,Facts,Provisions,Issue,Position,Formatter process
    class COLValidation,ThemeValidation,FinalReview decision
    class End output
```

### 3. Streamlit Web Application

**Location**: `cold_case_analyzer_agent/streamlit/`

The Streamlit application provides an interactive web interface with step-by-step guided analysis and user feedback integration.

#### Key Components:

- **Main App** (`app.py`): Application orchestration and configuration
- **Main Workflow** (`components/main_workflow.py`): Step-by-step processing coordination
- **UI Components** (`components/`): Modular interface components for each analysis phase
- **State Manager** (`utils/state_manager.py`): Session state and data persistence
- **Analysis Tools** (`tools/`): LLM integration and processing utilities

#### Component Architecture:

```mermaid
graph TB
    subgraph "Streamlit Application Structure"
        App[app.py<br/>Main Orchestrator]
        
        subgraph "Authentication & Config"
            Auth[Auth Component<br/>User Management]
            ModelSelector[Model Selector<br/>LLM Configuration]
            CSS[CSS Loader<br/>Styling]
            Sidebar[Sidebar<br/>Navigation]
        end
        
        subgraph "Main Workflow Components"
            MainWorkflow[Main Workflow<br/>Step Orchestration]
            InputHandler[Input Handler<br/>Case Input & Upload]
            JurisdictionDetect[Jurisdiction Detection<br/>Legal System ID]
            COLProcessor[COL Processor<br/>Section Extraction]
            ThemeClassifier[Theme Classifier<br/>PIL Theme Analysis]
            AnalysisWorkflow[Analysis Workflow<br/>Complete Analysis]
        end
        
        subgraph "Utilities"
            StateManager[State Manager<br/>Session Management]
            DataLoaders[Data Loaders<br/>Demo & Theme Data]
            PDFHandler[PDF Handler<br/>Document Processing]
            Database[Database<br/>Result Persistence]
        end
        
        subgraph "Analysis Tools"
            COLExtractor[COL Extractor<br/>Section Identification]
            ThemeExtractor[Theme Extractor<br/>Classification]
            AnalysisRunner[Analysis Runner<br/>LLM Orchestration]
        end
    end

    App --> Auth
    App --> ModelSelector
    App --> CSS
    App --> Sidebar
    App --> MainWorkflow
    
    MainWorkflow --> InputHandler
    MainWorkflow --> JurisdictionDetect
    MainWorkflow --> COLProcessor
    MainWorkflow --> ThemeClassifier
    MainWorkflow --> AnalysisWorkflow
    
    InputHandler --> PDFHandler
    InputHandler --> DataLoaders
    
    COLProcessor --> COLExtractor
    COLProcessor --> StateManager
    
    ThemeClassifier --> ThemeExtractor
    ThemeClassifier --> StateManager
    
    AnalysisWorkflow --> AnalysisRunner
    AnalysisWorkflow --> Database
    AnalysisWorkflow --> StateManager

    classDef main fill:#1976d2,color:white
    classDef auth fill:#7b1fa2,color:white
    classDef workflow fill:#388e3c,color:white
    classDef util fill:#f57c00,color:white
    classDef tool fill:#d32f2f,color:white

    class App main
    class Auth,ModelSelector,CSS,Sidebar auth
    class MainWorkflow,InputHandler,JurisdictionDetect,COLProcessor,ThemeClassifier,AnalysisWorkflow workflow
    class StateManager,DataLoaders,PDFHandler,Database util
    class COLExtractor,ThemeExtractor,AnalysisRunner tool
```

## Data Flow Patterns

### CLI Application Data Flow

```mermaid
flowchart TD
    subgraph "Input Phase"
        UserInput[User Selects:<br/>• Data Source<br/>• Model]
        DataFetch[Fetch Data:<br/>• cases.xlsx<br/>• concepts.xlsx<br/>• Airtable data]
    end
    
    subgraph "Processing Phase"
        CaseLoop[For Each Case]
        COLSection[Extract COL Section]
        Abstract[Extract Abstract]
        Facts[Extract Relevant Facts]
        Provisions[Extract PIL Provisions]
        Theme[Classify PIL Theme]
        Issue[Identify COL Issue]
        Position[Extract Court Position]
    end
    
    subgraph "Output Phase"
        Results[Compile Results]
        SaveCSV[Save to CSV]
        Evaluation[Optional Evaluation<br/>vs Ground Truth]
    end
    
    UserInput --> DataFetch
    DataFetch --> CaseLoop
    CaseLoop --> COLSection
    COLSection --> Abstract
    Abstract --> Facts
    Facts --> Provisions
    Provisions --> Theme
    Theme --> Issue
    Issue --> Position
    Position --> Results
    Results --> SaveCSV
    SaveCSV --> Evaluation

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e8,stroke:#388e3c

    class UserInput,DataFetch input
    class CaseLoop,COLSection,Abstract,Facts,Provisions,Theme,Issue,Position process
    class Results,SaveCSV,Evaluation output
```

### LangGraph Engine Data Flow

```mermaid
flowchart TD
    subgraph "Input & Initial Processing"
        CourtText[Court Decision Text]
        InitState[Initialize State Schema]
        TextNode[Text Input Node]
    end
    
    subgraph "Validation Loop 1: COL Section"
        COLExtract[COL Extraction Node]
        COLInterrupt[User COL Validation]
        COLApproved{Approved?}
        COLRefine[Refinement Feedback]
    end
    
    subgraph "Validation Loop 2: PIL Theme"  
        ThemeNode[Theme Classification Node]
        ThemeInterrupt[User Theme Validation]
        ThemeApproved{Approved?}
        ThemeRefine[Theme Refinement]
    end
    
    subgraph "Sequential Analysis"
        AbstractNode[Abstract Node]
        FactsNode[Relevant Facts Node]
        ProvisionsNode[PIL Provisions Node]
        IssueNode[COL Issue Node]
        PositionNode[Court Position Node]
    end
    
    subgraph "Final Review & Output"
        FormatNode[Format Results Node]
        FinalInterrupt[Final Review Interrupt]
        FinalApproved{Analysis Approved?}
        Complete[Analysis Complete]
    end

    CourtText --> InitState
    InitState --> TextNode
    TextNode --> COLExtract
    COLExtract --> COLInterrupt
    COLInterrupt --> COLApproved
    
    COLApproved -->|Yes| ThemeNode
    COLApproved -->|No| COLRefine
    COLRefine --> COLExtract
    
    ThemeNode --> ThemeInterrupt
    ThemeInterrupt --> ThemeApproved
    ThemeApproved -->|Yes| AbstractNode
    ThemeApproved -->|No| ThemeRefine
    ThemeRefine --> ThemeNode
    
    AbstractNode --> FactsNode
    FactsNode --> ProvisionsNode
    ProvisionsNode --> IssueNode
    IssueNode --> PositionNode
    PositionNode --> FormatNode
    
    FormatNode --> FinalInterrupt
    FinalInterrupt --> FinalApproved
    FinalApproved -->|Yes| Complete
    FinalApproved -->|No| FormatNode

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef validation fill:#fff3e0,stroke:#f57c00
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e8,stroke:#388e3c
    classDef decision fill:#ffebee,stroke:#d32f2f

    class CourtText,InitState,TextNode input
    class COLExtract,COLInterrupt,ThemeNode,ThemeInterrupt validation
    class AbstractNode,FactsNode,ProvisionsNode,IssueNode,PositionNode,FormatNode process
    class Complete output
    class COLApproved,ThemeApproved,FinalApproved decision
```

### Streamlit Application Data Flow

```mermaid
flowchart TD
    subgraph "User Input Phase"
        CaseCitation[Case Citation Input]
        TextInput[Court Decision Text<br/>• Manual Input<br/>• PDF Upload<br/>• Demo Case]
        Authentication[User Authentication]
        ModelSelect[Model Selection]
    end
    
    subgraph "Jurisdiction Phase"
        JurisdictDetect[Jurisdiction Detection]
        JurisdictConfirm[User Confirmation]
        JurisdictData[Final Jurisdiction Data]
    end
    
    subgraph "COL Processing Phase"
        COLExtraction[COL Section Extraction]
        COLDisplay[Display COL Sections]
        COLFeedback[User Feedback Collection]
        COLRefinement[Section Refinement]
    end
    
    subgraph "Theme Classification Phase"
        ThemeExtract[Theme Classification]
        ThemeDisplay[Display Themes]
        ThemeScore[User Theme Scoring]
        ThemeRefine[Theme Refinement]
    end
    
    subgraph "Complete Analysis Phase"
        FullAnalysis[Complete Case Analysis]
        ResultsDisplay[Display Full Results]
        UserFeedback[User Feedback]
        ResultsSave[Save to Database]
    end
    
    subgraph "State Management"
        SessionState[Streamlit Session State]
        StateUpdates[State Updates]
        StateRetrieval[State Retrieval]
    end

    CaseCitation --> JurisdictDetect
    TextInput --> JurisdictDetect
    Authentication --> ModelSelect
    ModelSelect --> JurisdictDetect
    
    JurisdictDetect --> JurisdictConfirm
    JurisdictConfirm --> JurisdictData
    JurisdictData --> COLExtraction
    
    COLExtraction --> COLDisplay
    COLDisplay --> COLFeedback
    COLFeedback --> COLRefinement
    COLRefinement --> ThemeExtract
    
    ThemeExtract --> ThemeDisplay
    ThemeDisplay --> ThemeScore
    ThemeScore --> ThemeRefine
    ThemeRefine --> FullAnalysis
    
    FullAnalysis --> ResultsDisplay
    ResultsDisplay --> UserFeedback
    UserFeedback --> ResultsSave
    
    %% State management connections
    COLExtraction --> SessionState
    ThemeExtract --> SessionState
    FullAnalysis --> SessionState
    SessionState --> StateUpdates
    StateUpdates --> StateRetrieval

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef feedback fill:#fff3e0,stroke:#f57c00
    classDef state fill:#e8f5e8,stroke:#388e3c
    classDef output fill:#fce4ec,stroke:#880e4f

    class CaseCitation,TextInput,Authentication,ModelSelect input
    class JurisdictDetect,COLExtraction,ThemeExtract,FullAnalysis process
    class JurisdictConfirm,COLFeedback,ThemeScore,UserFeedback feedback
    class SessionState,StateUpdates,StateRetrieval state
    class ResultsDisplay,ResultsSave output
```

## Data Models and Schema

### Core Analysis Schema

The system uses consistent data structures across all applications:

```python
# Core Case Analysis Result Schema
{
    "ID": str,                           # Case identifier
    "Quote": str,                        # Choice of Law section
    "Abstract": str,                     # Case abstract/summary
    "Relevant facts / Summary": str,     # Factual background
    "PIL provisions": List[str],         # Legal provisions
    "Themes": List[str],                 # PIL themes
    "Choice of law issue": str,          # Main legal issue
    "Court's position": str,             # Court's ruling
    "processing_time": str               # Analysis duration
}
```

### LangGraph State Schema

```python
# LangGraph CourtAnalysisSchema
class CourtAnalysisSchema(TypedDict):
    full_text: str                       # Input court decision
    quote: Optional[str]                 # COL section
    themes_table: str                    # Available themes
    themes_table_data: Dict[str, str]    # Theme definitions
    classification: Optional[List[str]]   # Theme classifications
    user_approved_col: Optional[bool]    # COL validation
    user_approved_theme: Optional[bool]  # Theme validation
    abstract: Optional[str]              # Extracted abstract
    relevant_facts: Optional[str]        # Relevant facts
    pil_provisions: Optional[List[str]]  # PIL provisions
    col_issue: Optional[str]             # COL issue
    courts_position: Optional[str]       # Court position
    formatted_analysis: Optional[str]    # Final formatted result
    goto_node: Optional[str]             # Routing control
```

### Streamlit State Schema

```python
# Streamlit Session State Structure
{
    "col_state": {
        "case_citation": str,
        "username": str,
        "model": str,
        "full_text": str,
        "col_section": List[str],
        "col_section_feedback": List[str],
        "col_section_eval_iter": int,
        "jurisdiction": str,
        "precise_jurisdiction": str,
        "jurisdiction_eval_score": float,
        "theme_first_score_submitted": bool,
        "theme_classifications": List[str],
        "theme_feedback": str,
        "analysis_complete": bool,
        "final_analysis": Dict[str, str],
        "user_email": Optional[str]
    }
}
```

## Component Interactions

### LLM Handler Integration

All applications share a common LLM handler that provides standardized access to language models:

```mermaid
graph TB
    subgraph "Applications"
        CLI[CLI Case Analyzer]
        LangGraph[LangGraph Engine]
        Streamlit[Streamlit App]
    end
    
    subgraph "LLM Handler Layer"
        ModelAccess[Model Access<br/>llm_handler/model_access.py]
        PromptManager[Prompt Manager<br/>Template Loading]
        ConfigLoader[Config Loader<br/>API Keys & Settings]
    end
    
    subgraph "External APIs"
        OpenAI[OpenAI API<br/>gpt-4o, gpt-4o-mini]
        LlamaAPI[Llama API<br/>llama3.1]
    end
    
    CLI --> ModelAccess
    LangGraph --> ModelAccess
    Streamlit --> ModelAccess
    
    ModelAccess --> PromptManager
    ModelAccess --> ConfigLoader
    
    ModelAccess --> OpenAI
    ModelAccess --> LlamaAPI

    classDef app fill:#1976d2,color:white
    classDef handler fill:#388e3c,color:white
    classDef api fill:#d32f2f,color:white

    class CLI,LangGraph,Streamlit app
    class ModelAccess,PromptManager,ConfigLoader handler
    class OpenAI,LlamaAPI api
```

### Data Source Integration

The system supports multiple data sources with a unified interface:

```mermaid
graph TB
    subgraph "Data Sources"
        LocalExcel[Local Excel Files<br/>cases.xlsx, concepts.xlsx]
        AirtableDB[Airtable Database<br/>Remote Data]
        DemoData[Demo Case Data<br/>BGE 132 III 285]
        GroundTruth[Ground Truth CSV<br/>Evaluation Data]
    end
    
    subgraph "Data Handlers"
        LocalHandler[Local File Handler<br/>data_handler/local_file_retrieval.py]
        AirtableHandler[Airtable Handler<br/>data_handler/airtable_retrieval.py]
        DemoLoader[Demo Loader<br/>utils/data_loaders.py]
    end
    
    subgraph "Applications"
        CLIApp[CLI Application]
        StreamlitApp[Streamlit App]
        EvaluationSystem[Evaluation System]
    end

    LocalExcel --> LocalHandler
    AirtableDB --> AirtableHandler
    DemoData --> DemoLoader
    GroundTruth --> LocalHandler
    
    LocalHandler --> CLIApp
    AirtableHandler --> CLIApp
    DemoLoader --> StreamlitApp
    LocalHandler --> EvaluationSystem

    classDef data fill:#e8f5e8,stroke:#388e3c
    classDef handler fill:#fff3e0,stroke:#f57c00
    classDef app fill:#e3f2fd,stroke:#1976d2

    class LocalExcel,AirtableDB,DemoData,GroundTruth data
    class LocalHandler,AirtableHandler,DemoLoader handler
    class CLIApp,StreamlitApp,EvaluationSystem app
```

## Setup and Configuration

### Environment Configuration

The system uses environment variables for configuration management:

```bash
# Required for LLM functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional for alternative LLM
LLAMA_API_KEY=your_llama_api_key_here

# Optional for Airtable data source
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_CD_TABLE=your_table_name
AIRTABLE_CONCEPTS_TABLE=your_concepts_table

# Optional for Streamlit authentication
USER_CREDENTIALS={"username":"password"}

# Optional for database persistence
SQL_CONN_STRING=postgresql://user:pass@host:port/db
```

### Directory Structure

```
cold-case-analysis/
├── README.md                           # Main project documentation
├── requirements.txt                    # Python dependencies for CLI
├── blueprint.env                       # Environment template
├── docs/                               # Documentation
│   ├── ARCHITECTURE.md                 # This document
│   └── agent.md                        # Agent workflow documentation
├── cold_case_analyzer/                 # CLI Application
│   ├── main.py                         # CLI entry point
│   ├── config.py                       # Configuration management
│   ├── case_analyzer/                  # Core analysis logic
│   ├── data_handler/                   # Data source handlers
│   ├── evaluator/                      # Result evaluation
│   ├── llm_handler/                    # LLM integration
│   ├── visualizer/                     # Result visualization
│   ├── cca_langgraph/                  # LangGraph engine
│   │   ├── main.py                     # LangGraph entry point
│   │   ├── graph_config.py             # Workflow configuration
│   │   ├── nodes/                      # Analysis nodes
│   │   ├── tools/                      # Analysis tools
│   │   └── prompts/                    # LangGraph prompts
│   ├── data/                           # Input/output data
│   │   ├── cases.xlsx                  # Input cases
│   │   ├── concepts.xlsx               # PIL concepts
│   │   └── ground_truth.csv            # Evaluation reference
│   └── prompts/                        # Analysis prompts
├── cold_case_analyzer_agent/           # Web Application
│   ├── streamlit/                      # Streamlit app
│   │   ├── app.py                      # Web app entry point
│   │   ├── requirements.txt            # Web app dependencies
│   │   ├── components/                 # UI components
│   │   ├── utils/                      # Utility functions
│   │   ├── tools/                      # Analysis tools
│   │   ├── prompts/                    # Streamlit prompts
│   │   └── tests/                      # Test suite
│   └── app_requirements.md             # Full-stack architecture spec
└── 5_IPR_Nachwuchstagung/             # Presentation materials
```

### Installation and Setup

1. **Environment Setup**:
   ```bash
   cp blueprint.env .env
   # Edit .env with your API keys
   ```

2. **CLI Application**:
   ```bash
   pip install -r requirements.txt
   python cold_case_analyzer/main.py
   ```

3. **LangGraph Engine**:
   ```bash
   cd cold_case_analyzer/cca_langgraph
   python main.py
   ```

4. **Streamlit Web App**:
   ```bash
   cd cold_case_analyzer_agent/streamlit
   pip install pymupdf4llm psycopg2-binary
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

This documentation provides a comprehensive overview of the Cold Case Analysis system architecture and data flow patterns. Each component is designed to work independently while sharing common utilities and following consistent data schemas.