# CoLD Case Analyzer - Architecture and Data Flow Documentation

This document provides a comprehensive overview of the CoLD Case Analyzer project structure, data flow patterns, and component interactions.

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Application Components](#application-components)
- [Data Flow Patterns](#data-flow-patterns)
- [Data Models and Schema](#data-models-and-schema)
- [Setup and Configuration](#setup-and-configuration)

## Project Overview

The CoLD Case Analyzer is a Streamlit-based web application that leverages Large Language Models (LLMs) to analyze court decisions concerning choice of law (COL) in international commercial contracts. The system provides an interactive interface for step-by-step analysis with human validation at each stage.

### Key Features

- **Interactive Workflow**: User-guided analysis with validation at each step
- **Jurisdiction Detection**: Identifies legal system (Civil Law, Common Law, or Indian law)
- **COL Extraction**: Extracts relevant Choice of Law sections
- **Theme Classification**: Categorizes cases against PIL taxonomy
- **Comprehensive Analysis**: Extracts abstract, facts, provisions, issues, and court positions
- **Database Persistence**: Optional PostgreSQL storage for analyses
- **Multi-jurisdiction Support**: Specialized prompts for different legal systems

## System Architecture

```mermaid
graph TB
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT Models]
        PostgreSQL[(PostgreSQL<br/>Optional Storage)]
        Airtable[Airtable API<br/>LATAM Module]
    end

    subgraph "CoLD Case Analyzer"
        subgraph "Streamlit Application"
            App[Main App<br/>app.py]
            
            subgraph "Components Layer"
                Auth[Authentication<br/>Model Selection]
                Input[Input Handler<br/>PDF/Text/Demo]
                Jurisdiction[Jurisdiction<br/>Detection]
                COL[COL Processor<br/>Extraction]
                Theme[Themes<br/>Classification]
                Confidence[Confidence Display<br/>Scoring]
                PIL[PIL Provisions<br/>Handler]
                Analysis[Analysis Workflow<br/>Orchestration]
                MainWF[Main Workflow<br/>Coordinator]
                Sidebar[Sidebar<br/>Navigation]
                CSS[CSS<br/>Styling]
            end
            
            subgraph "Tools Layer"
                CaseAnalyzer[Case Analyzer<br/>Core Logic]
                COLExtractor[COL Extractor<br/>Extraction Tool]
                JurDetector[Jurisdiction<br/>Detector]
                JurClassifier[Jurisdiction<br/>Classifier]
                ThemeClassifier[Theme Classifier<br/>Classification Tool]
                AbstractGen[Abstract<br/>Generator]
                FactsExt[Relevant Facts<br/>Extractor]
                PILProvExt[PIL Provisions<br/>Extractor]
                IssueExt[COL Issue<br/>Extractor]
                PositionExt[Court Position<br/>Extractor]
                ObiterExt[Obiter Dicta<br/>Extractor]
                DissentExt[Dissenting Opinions<br/>Extractor]
                CitationExt[Case Citation<br/>Extractor]
            end
            
            subgraph "Utilities Layer"
                StateManager[State Manager<br/>Session State]
                DataLoaders[Data Loaders<br/>Themes/Demos]
                PDFHandler[PDF Handler<br/>Text Extraction]
                PromptSelector[Prompt Selector<br/>Jurisdiction-based]
                SystemPromptGen[System Prompt<br/>Generator]
                DebugPrint[Debug Print<br/>State]
                SampleCD[Sample CD<br/>Demo Data]
            end
            
            subgraph "Prompts Library"
                CivilLaw[Civil Law<br/>Prompts]
                CommonLaw[Common Law<br/>Prompts]
                India[India<br/>Prompts]
                System[System-Level<br/>Prompts]
            end
        end
        
        subgraph "LATAM Module"
            PDFExtractor[PDF Extractor<br/>Airtable Download]
            TXTConverter[TXT Converter<br/>Format Conversion]
        end
    end

    subgraph "Data Sources"
        LocalData[Local Data<br/>themes.csv<br/>jurisdictions.csv]
        DemoCase[Demo Case<br/>BGE 132 III 285]
    end

    %% External connections
    App --> OpenAI
    App --> PostgreSQL
    PDFExtractor --> Airtable
    
    %% Component connections
    App --> MainWF
    MainWF --> Auth
    MainWF --> Input
    MainWF --> Jurisdiction
    MainWF --> COL
    MainWF --> Theme
    MainWF --> PIL
    MainWF --> Analysis
    
    %% Tools usage
    Jurisdiction --> JurDetector
    COL --> COLExtractor
    Theme --> ThemeClassifier
    Analysis --> CaseAnalyzer
    
    %% Utilities usage
    Auth --> StateManager
    Input --> PDFHandler
    Input --> DataLoaders
    Jurisdiction --> PromptSelector
    COL --> PromptSelector
    Theme --> PromptSelector
    Analysis --> PromptSelector
    
    %% Prompts usage
    PromptSelector --> CivilLaw
    PromptSelector --> CommonLaw
    PromptSelector --> India
    PromptSelector --> System
    
    %% Data access
    DataLoaders --> LocalData
    DataLoaders --> DemoCase
    
    classDef external fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef app fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef component fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef tool fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class OpenAI,PostgreSQL,Airtable external
    class App,MainWF app
    class Auth,Input,Jurisdiction,COL,Theme,PIL,Analysis component
    class CaseAnalyzer,COLExtractor,JurDetector,ThemeClassifier tool
    class LocalData,DemoCase data
```
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

## Application Components

### Streamlit Web Application

**Location**: `src/`

The Streamlit application provides an interactive web interface for analyzing court decisions with step-by-step user validation and feedback.

#### Application Structure:

**Entry Point**:
- `app.py`: Main application initialization, page config, authentication, and workflow rendering

**Components** (`components/`):
- `auth.py`: Authentication and model selection
- `input_handler.py`: Case citation, PDF upload, text input, demo case loading
- `jurisdiction.py`: Enhanced jurisdiction detection with precise jurisdiction identification
- `col_processor.py`: Choice of Law section extraction and validation
- `themes.py`: PIL theme classification and scoring
- `confidence_display.py`: Confidence score display with reasoning
- `pil_provisions_handler.py`: PIL provisions extraction
- `analysis_workflow.py`: Main analysis execution and step management
- `main_workflow.py`: Overall workflow orchestration
- `sidebar.py`: Sidebar navigation and information
- `css.py`: Custom styling
- `database.py`: PostgreSQL persistence

**Tools** (`tools/`):
- `case_analyzer.py`: Core case analysis logic with LLM integration
- `col_extractor.py`: COL section extraction tool
- `jurisdiction_detector.py`: Jurisdiction detection logic
- `jurisdiction_classifier.py`: Precise jurisdiction identification with confidence
- `theme_classifier.py`: Theme classification tool
- `abstract_generator.py`: Abstract generation from analysis results
- `relevant_facts_extractor.py`: Relevant facts extraction
- `pil_provisions_extractor.py`: PIL provisions extraction
- `col_issue_extractor.py`: Choice of Law issue identification
- `courts_position_extractor.py`: Court position extraction
- `obiter_dicta_extractor.py`: Obiter dicta extraction (Common Law only)
- `dissenting_opinions_extractor.py`: Dissenting opinions extraction (Common Law only)
- `case_citation_extractor.py`: Case citation extraction and normalization

**Utilities** (`utils/`):
- `state_manager.py`: Session state management
- `data_loaders.py`: Data loading (themes, demo cases)
- `pdf_handler.py`: PDF text extraction
- `themes_extractor.py`: Theme extraction utilities
- `system_prompt_generator.py`: Jurisdiction-specific prompt generation
- `debug_print_state.py`: Debug utilities for printing session state
- `sample_cd.py`: Sample court decision data for testing

**Prompts** (`prompts/`):
- `civil_law/`: Civil law jurisdiction prompts
- `common_law/`: Common law jurisdiction prompts
- `india/`: Indian law jurisdiction prompts
- `legal_system_type_detection.py`: System-level detection prompts
- `precise_jurisdiction_detection_prompt.py`: Precise jurisdiction prompts
- `prompt_selector.py`: Jurisdiction-based prompt selection

**Data** (`data/`):
- `themes.csv`: PIL theme taxonomy
- `jurisdictions.csv`: Jurisdiction reference data

#### Processing Flow:

```mermaid
sequenceDiagram
    participant User
    participant App as Streamlit App
    participant Components as UI Components
    participant Tools as Analysis Tools
    participant LLM as OpenAI API
    participant DB as PostgreSQL

    User->>App: Access application
    App->>Components: Render input phase
    User->>Components: Enter citation & text/PDF
    
    User->>Components: Click "Detect Jurisdiction"
    Components->>Tools: Detect jurisdiction
    Tools->>LLM: Analyze court decision
    LLM->>Tools: Return jurisdiction
    Tools->>Components: Display results
    User->>Components: Confirm/Override jurisdiction

    User->>Components: Proceed to COL extraction
    Components->>Tools: Extract COL sections
    Tools->>LLM: Identify COL content
    LLM->>Tools: Return COL sections
    Tools->>Components: Display extractions
    User->>Components: Edit COL sections if needed

    User->>Components: Proceed to theme classification
    Components->>Tools: Classify PIL themes
    Tools->>LLM: Categorize against taxonomy
    LLM->>Tools: Return themes
    Tools->>Components: Display themes
    User->>Components: Edit themes if needed

    User->>Components: Proceed to detailed analysis
    Note over Components,Tools: Parallel execution where possible
    Components->>Tools: Execute all analysis steps
    Tools->>LLM: Generate analysis (Facts, PIL, Issue, Position, Abstract)
    LLM->>Tools: Return results
    Tools->>Components: Display all results for final editing

    User->>Components: Review and edit all results
    User->>Components: Submit final analysis

    Components->>DB: Save complete analysis
    DB->>Components: Confirm save
    Components->>User: Display completion message
```

**Location**: `cold_case_analyzer/cca_langgraph/`

The LangGraph engine provides advanced workflow orchestration with human-in-the-loop capabilities using a graph-based approach.

#### Key Components:

- **Graph Configuration** (`graph_config.py`): Node definitions and workflow orchestration
- **Analysis Nodes** (`nodes/`): Individual processing steps (COL extraction, theme classification, etc.)
- **Analysis Tools** (`tools/`): LLM integration utilities
- **Interrupt Handlers** (`nodes/interrupt_handler.py`): Human validation checkpoints

#### Workflow Architecture:

### LATAM Case Analysis Module

**Location**: `latam_case_analysis/`

A specialized module for processing Latin American court cases with Airtable integration.

#### Components:

- `pdf_extractor.py`: Downloads PDFs from Airtable for South & Latin America region cases
- `txt_converter.py`: Converts downloaded PDFs to text format for analysis

#### Usage:

```python
# Set environment variables
export AIRTABLE_API_KEY="your_key"
export AIRTABLE_BASE_ID="base_id"

# Download PDFs from Airtable
python latam_case_analysis/pdf_extractor.py

# Convert to text
python latam_case_analysis/txt_converter.py
```

This module integrates with Airtable's Court Decisions table and filters records by region for targeted data extraction.

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
            JurisdictionDetect[Jurisdiction<br/>Legal System ID]
            COLProcessor[COL Processor<br/>Section Extraction]
            ThemesComponent[Themes<br/>PIL Theme Analysis]
            ConfidenceDisplay[Confidence Display<br/>Score & Reasoning]
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
    MainWorkflow --> ThemesComponent
    MainWorkflow --> ConfidenceDisplay
    MainWorkflow --> AnalysisWorkflow
    
    InputHandler --> PDFHandler
    InputHandler --> DataLoaders
    
    COLProcessor --> COLExtractor
    COLProcessor --> StateManager
    
    ThemesComponent --> ThemeExtractor
    ThemesComponent --> StateManager
    
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
    class MainWorkflow,InputHandler,JurisdictionDetect,COLProcessor,ThemesComponent,ConfidenceDisplay,AnalysisWorkflow workflow
    class StateManager,DataLoaders,PDFHandler,Database util
    class COLExtractor,ThemeExtractor,AnalysisRunner tool
```

## Data Flow Patterns

### User Interaction Flow

```mermaid
flowchart TD
    Start([User Opens App]) --> Input[Input Phase]
    
    subgraph Input[Input Phase]
        Citation[Enter Case Citation]
        Upload[Upload PDF or Enter Text]
        Demo[Or Use Demo Case]
    end
    
    Input --> Jurisdiction[Jurisdiction Detection]

    subgraph Jurisdiction[Jurisdiction Detection]
        Detect[Detect Legal System]
        JurisConfirm[Confirm/Override if Needed]
    end

    Jurisdiction --> COLExtract[COL Extraction]

    subgraph COLExtract[COL Section Extraction]
        ExtractCOL[Extract COL Sections]
        COLEdit[Edit if Needed]
    end

    COLExtract --> ThemeClass[Theme Classification]

    subgraph ThemeClass[Theme Classification]
        ClassifyTheme[Classify PIL Themes]
        ThemeEdit[Edit if Needed]
    end

    ThemeClass --> Analysis[Parallel Analysis]

    subgraph Analysis[Parallel Analysis Execution]
        ParallelSteps[Parallel: Facts, PIL, Issue]
        SequentialSteps[Sequential: Position, Abstract]
        FinalEdit[Final Edit All Results]
    end
        Issue[4. COL Issue]
        Position[5. Court Position]
    end
    
    Analysis --> Save[Save to Database]
    Save --> Complete([Analysis Complete])
    
    classDef phase fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef step fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    Analysis --> Save[Save to Database]
    Save --> Complete([Analysis Complete])

    classDef phase fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef step fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class Input,Jurisdiction,COLExtract,ThemeClass,Analysis phase
    class ParallelSteps,SequentialSteps,FinalEdit step
```

### LLM Integration Data Flow

```mermaid
flowchart LR
    subgraph "User Input"
        Text[Court Decision<br/>Text/PDF]
        Citation[Case Citation]
        Jurisdiction[Jurisdiction Info]
    end
    
    subgraph "Prompt Generation"
        PromptSelector[Prompt Selector]
        CivilLaw[Civil Law Prompts]
        CommonLaw[Common Law Prompts]
        India[India Prompts]
    end
    
    subgraph "LLM Processing"
        OpenAI[OpenAI API]
        Context[Context:<br/>• Decision Text<br/>• Jurisdiction<br/>• Previous Results]
        Response[LLM Response]
    end
    
    subgraph "Result Processing"
        Parse[Parse Response]
        Validate[Validate Format]
        Store[Store in State]
    end
    
    subgraph "User Review"
        Display[Display to User]
        Edit[User Edits if Needed]
        Approve[Approve/Continue]
    end

    Text --> PromptSelector
    Citation --> PromptSelector
    Jurisdiction --> PromptSelector

    PromptSelector --> CivilLaw
    PromptSelector --> CommonLaw
    PromptSelector --> India

    CivilLaw --> Context
    CommonLaw --> Context
    India --> Context

    Context --> OpenAI
    OpenAI --> Response
    Response --> Parse
    Parse --> Validate
    Validate --> Store
    Store --> Display
    Display --> Edit
    Edit --> Approve

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef prompt fill:#f3e5f5,stroke:#7b1fa2
    classDef llm fill:#fff3e0,stroke:#f57c00
    classDef process fill:#e8f5e9,stroke:#388e3c
    classDef user fill:#fce4ec,stroke:#c2185b

    class Text,Citation,Jurisdiction input
    class PromptSelector,CivilLaw,CommonLaw,India prompt
    class OpenAI,Context,Response llm
    class Parse,Validate,Store process
    class Display,Edit,Approve user
```

### State Management Data Flow

### State Management Data Flow

```mermaid
flowchart TD
    subgraph "Streamlit Session"
        InitState[Initialize State<br/>initialize_col_state]
        SessionDict[st.session_state Dictionary]
    end
    
    subgraph "State Keys"
        CaseCit[case_citation]
        FullText[full_text_input]
        Juris[jurisdiction]
        COLData[col_sections]
        Themes[themes_data]
        AnalysisData[analysis_results]
    end

    subgraph "State Operations"
        Update[Update State<br/>st.session_state.key = value]
        Retrieve[Retrieve State<br/>value = st.session_state.key]
        Check[Check Existence<br/>if key in st.session_state]
    end

    subgraph "Component Access"
        InputComp[Input Components]
        ProcComp[Processing Components]
        DispComp[Display Components]
    end

    InitState --> SessionDict
    SessionDict --> CaseCit
    SessionDict --> FullText
    SessionDict --> Juris
    SessionDict --> COLData
    SessionDict --> Themes
    SessionDict --> AnalysisData

    CaseCit --> Update
    FullText --> Update
    Juris --> Update
    COLData --> Update
    Themes --> Update
    AnalysisData --> Update

    Update --> Retrieve
    Retrieve --> Check

    Check --> InputComp
    Check --> ProcComp
    Check --> DispComp

    InputComp --> Update
    ProcComp --> Update
    DispComp --> Retrieve

    classDef session fill:#e3f2fd,stroke:#1976d2
    classDef keys fill:#f3e5f5,stroke:#7b1fa2
    classDef ops fill:#fff3e0,stroke:#f57c00
    classDef comp fill:#e8f5e9,stroke:#388e3c

    class InitState,SessionDict session
    class CaseCit,FullText,Juris,COLData,Themes,AnalysisData keys
    class Update,Retrieve,Check ops
    class InputComp,ProcComp,DispComp comp
```

## Data Models and Schema

### Core Analysis Schema

The system uses consistent data structures for case analysis:

```python
# Complete Case Analysis Result
{
    "case_citation": str,                # Case identification
    "jurisdiction": str,                 # Legal system (Civil Law/Common Law/India)
    "col_sections": List[str],           # Choice of Law sections extracted
    "themes": List[str],                 # PIL themes classified
    "abstract": str,                     # Case abstract/summary
    "relevant_facts": str,               # Factual background
    "pil_provisions": List[str],         # Legal provisions cited
    "themes": List[str],                 # PIL themes classified
    "col_issue": str,                    # Choice of Law issue identified
    "courts_position": str,              # Court's reasoning and position
    "user_email": Optional[str],         # Optional user contact
    "username": Optional[str],           # User identification
    "model": str,                        # LLM model used
    "timestamp": datetime                # Analysis timestamp
}
```

### Session State Structure

```python
# Streamlit Session State Keys
{
    # Input Phase
    "case_citation": str,
    "full_text_input": str,
    "user_email": str,
    
    # Authentication
    "authenticated": bool,
    "username": str,
    "selected_model": str,
    
    # Jurisdiction Detection
    "jurisdiction": str,
    "precise_jurisdiction": str,
    "jurisdiction_detected": bool,
    "jurisdiction_confirmed": bool,

    # COL Processing
    "col_sections": List[str],
    "col_section_feedback": List[str],
    "col_done": bool,

    # Theme Classification
    "themes_data": List[str],
    "theme_done": bool,

    # Analysis Results
    "analysis_results": Dict[str, str],
    "analysis_done": bool,
    "parallel_execution_started": bool,
    
    # Demo Case
    "demo_case_loaded": bool
}
```

### Database Schema

```python
# PostgreSQL Table Structure (optional)
{
    "id": SERIAL PRIMARY KEY,
    "case_citation": TEXT,
    "username": TEXT,
    "user_email": TEXT,
    "model": TEXT,
    "jurisdiction": TEXT,
    "col_sections": JSONB,
    "themes": JSONB,
    "abstract": TEXT,
    "relevant_facts": TEXT,
    "pil_provisions": JSONB,
    "col_issue": TEXT,
    "courts_position": TEXT,
    "created_at": TIMESTAMP,
    "updated_at": TIMESTAMP
}
```

## LLM Integration

The application integrates with OpenAI's API for language model processing:

```mermaid
graph TB
    subgraph "Application Layer"
        Components[UI Components]
        Tools[Analysis Tools]
    end
    
    subgraph "Prompt Layer"
        PromptSelector[Prompt Selector<br/>prompt_selector.py]
        CivilLaw[Civil Law Prompts]
        CommonLaw[Common Law Prompts]
        India[India Prompts]
        SystemPrompts[System Prompts]
    end
    
    subgraph "LLM Layer"
        LangChain[LangChain<br/>langchain-openai]
        Config[Config Manager<br/>config.py]
    end
    
    subgraph "External API"
        OpenAI[OpenAI API<br/>GPT Models]
    end
    
    Components --> Tools
    Tools --> PromptSelector
    
    PromptSelector --> CivilLaw
    PromptSelector --> CommonLaw
    PromptSelector --> India
    PromptSelector --> SystemPrompts
    
    CivilLaw --> LangChain
    CommonLaw --> LangChain
    India --> LangChain
    SystemPrompts --> LangChain
    
    LangChain --> Config
    Config --> OpenAI

    classDef app fill:#e3f2fd,stroke:#1976d2
    classDef prompt fill:#f3e5f5,stroke:#7b1fa2
    classDef llm fill:#fff3e0,stroke:#f57c00
    classDef api fill:#ffebee,stroke:#d32f2f

    class Components,Tools app
    class PromptSelector,CivilLaw,CommonLaw,India,SystemPrompts prompt
    class LangChain,Config llm
    class OpenAI api
```

### Data Source Integration

The system integrates with multiple data sources:

```mermaid
graph TB
    subgraph "Data Sources"
        LocalCSV[Local CSV Files<br/>themes.csv<br/>jurisdictions.csv]
        DemoData[Demo Case Data<br/>BGE 132 III 285]
        AirtableDB[Airtable Database<br/>LATAM Module Only]
    end
    
    subgraph "Data Loaders"
        ThemeLoader[Theme Loader<br/>load_valid_themes]
        DemoLoader[Demo Loader<br/>get_demo_case_text]
        AirtableExtractor[PDF Extractor<br/>latam_case_analysis]
    end
    
    subgraph "Application"
        StreamlitApp[Streamlit Application]
        LATAMModule[LATAM Processing Module]
    end

    LocalCSV --> ThemeLoader
    DemoData --> DemoLoader
    AirtableDB --> AirtableExtractor
    
    ThemeLoader --> StreamlitApp
    DemoLoader --> StreamlitApp
    AirtableExtractor --> LATAMModule

    classDef data fill:#e8f5e9,stroke:#388e3c
    classDef loader fill:#fff3e0,stroke:#f57c00
    classDef app fill:#e3f2fd,stroke:#1976d2

    class LocalCSV,DemoData,AirtableDB data
    class ThemeLoader,DemoLoader,AirtableExtractor loader
    class StreamlitApp,LATAMModule app
```

## Setup and Configuration

### Environment Configuration

The system uses environment variables for configuration management:

```bash
# Required Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-nano  # Or your preferred model

# Optional Database Configuration
SQL_CONN_STRING=postgresql+psycopg2://user:pass@host:port/db
POSTGRESQL_HOST=your_host
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=your_database
POSTGRESQL_USERNAME=your_username
POSTGRESQL_PASSWORD=your_password

# Optional Authentication
USER_CREDENTIALS='{"username":"password","admin":"admin123"}'

# Optional LATAM Module (Airtable Integration)
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_CONCEPTS_TABLE=your_concepts_table

# Optional NoCode Database
NOCODB_BASE_URL=https://your-nocodb-instance/api/v1/db/data/noco/project_id
NOCODB_API_TOKEN=your_nocodb_token
NOCODB_POSTGRES_SCHEMA=your_schema_id
```

### Directory Structure

```
cold-case-analysis/
├── README.md                           # Main project documentation
├── pyproject.toml                      # Python project configuration
├── uv.lock                             # Dependency lock file
├── .env.example                        # Environment template
├── Dockerfile                          # Docker deployment
├── docs/                               # Documentation
│   ├── ARCHITECTURE.md                 # This document
│   ├── QUICK_START.md                  # Quick start guide
│   ├── WORKFLOWS.md                    # Workflow documentation
│   ├── agent.md                        # Agent workflow details
│   └── DYNAMIC_SYSTEM_PROMPTS_README.md  # Prompts documentation
├── src/                                # Main application
│   ├── app.py                          # Streamlit app entry point
│   ├── config.py                       # Configuration management
│   ├── components/                     # UI components
│   │   ├── auth.py                     # Authentication
│   │   ├── input_handler.py            # Input handling
│   │   ├── jurisdiction.py             # Jurisdiction detection
│   │   ├── col_processor.py            # COL processing
│   │   ├── themes.py                   # Theme classification
│   │   ├── confidence_display.py       # Confidence display
│   │   ├── pil_provisions_handler.py   # PIL provisions
│   │   ├── analysis_workflow.py        # Analysis workflow
│   │   ├── main_workflow.py            # Main orchestration
│   │   ├── sidebar.py                  # Sidebar component
│   │   ├── css.py                      # Custom styling
│   │   └── database.py                 # Database persistence
│   ├── tools/                          # Analysis tools
│   │   ├── case_analyzer.py            # Core analyzer
│   │   ├── col_extractor.py            # COL extraction
│   │   ├── jurisdiction_detector.py    # Jurisdiction detection
│   │   ├── jurisdiction_classifier.py  # Precise jurisdiction classification
│   │   ├── theme_classifier.py         # Theme classification
│   │   ├── abstract_generator.py       # Abstract generation
│   │   ├── relevant_facts_extractor.py # Facts extraction
│   │   ├── pil_provisions_extractor.py # PIL provisions
│   │   ├── col_issue_extractor.py      # COL issue extraction
│   │   ├── courts_position_extractor.py  # Court position
│   │   ├── obiter_dicta_extractor.py   # Obiter dicta (Common Law)
│   │   ├── dissenting_opinions_extractor.py  # Dissenting opinions (Common Law)
│   │   └── case_citation_extractor.py  # Citation extraction
│   ├── utils/                          # Utility functions
│   │   ├── state_manager.py            # State management
│   │   ├── data_loaders.py             # Data loading
│   │   ├── pdf_handler.py              # PDF processing
│   │   ├── themes_extractor.py         # Theme extraction
│   │   ├── system_prompt_generator.py  # Dynamic prompt generation
│   │   ├── debug_print_state.py        # Debug utilities
│   │   └── sample_cd.py                # Sample court decision
│   ├── prompts/                        # Prompt templates
│   │   ├── civil_law/                  # Civil law prompts
│   │   ├── common_law/                 # Common law prompts
│   │   ├── india/                      # India prompts
│   │   ├── legal_system_type_detection.py  # Detection prompts
│   │   └── prompt_selector.py          # Prompt selection
│   ├── data/                           # Application data
│   │   ├── themes.csv                  # PIL theme taxonomy
│   │   └── jurisdictions.csv           # Jurisdiction data
│   └── tests/                          # Test suite
├── latam_case_analysis/                # LATAM module
│   ├── pdf_extractor.py                # PDF extraction from Airtable
│   └── txt_converter.py                # Text conversion
└── .streamlit/                         # Streamlit configuration
```

### Installation and Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/Choice-of-Law-Dataverse/cold-case-analysis.git
   cd cold-case-analysis
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY
   ```

3. **Install Dependencies**:

   Using pip:
   ```bash
   pip install streamlit langchain-core langchain-openai pandas pymupdf4llm psycopg2-binary python-dotenv requests
   ```

   Or using uv (recommended):
   ```bash
   uv sync
   ```

4. **Run Application**:
   ```bash
   # With pip
   cd src
   streamlit run app.py
   
   # With uv
   uv run streamlit run src/app.py
   ```

5. **Access Application**:
   - Open browser to `http://localhost:8501`
   - Click "Use Demo Case" to try the BGE 132 III 285 example

### Docker Deployment

```bash
# Build image
docker build -t cold-case-analyzer .

# Run container
docker run -p 8501:8501 --env-file .env cold-case-analyzer
```

## Summary

The CoLD Case Analyzer is a comprehensive Streamlit-based application for analyzing court decisions related to private international law. It provides:

- **Interactive Analysis**: Step-by-step workflow with user validation at key checkpoints
- **Multi-jurisdiction Support**: Specialized prompts for civil law, common law, and Indian legal systems
- **Comprehensive Extraction**: Jurisdiction, COL sections, themes, provisions, and detailed analysis
- **Parallel Processing**: Automated analysis with parallel execution for efficiency
- **Streamlined Editing**: Final review phase where all results can be edited at once
- **Optional Persistence**: PostgreSQL database integration
- **LATAM Module**: Specialized tools for Latin American case processing

The modular architecture with separate components, tools, utilities, and jurisdiction-specific prompts allows for easy maintenance and extension. The system integrates with OpenAI's API for language model processing and supports optional database persistence for storing analysis results.

For detailed workflow information, see [WORKFLOWS.md](WORKFLOWS.md). For quick start instructions, see [QUICK_START.md](QUICK_START.md).