# CoLD Case Analyzer - Workflow Documentation

This document provides detailed workflow diagrams and data flow patterns for the CoLD Case Analyzer Streamlit application.

## High-Level System Overview

```mermaid
graph TB
    User[Legal Analyst/<br/>Researcher]

    subgraph "CoLD Case Analyzer"
        WebUI[Streamlit<br/>Web Application]
    end

    subgraph "Core Components"
        PromptEngine[Prompt Engine<br/>Jurisdiction-Specific]
        AnalysisCore[Analysis Core<br/>Case Processing]
        StateManager[State Manager<br/>Session State]
    end

    subgraph "Data Layer"
        LocalData[Local CSV Files<br/>themes.csv<br/>jurisdictions.csv]
        DemoCase[Demo Case<br/>BGE 132 III 285]
        ResultsDB[(Optional PostgreSQL<br/>Results Storage)]
    end

    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT Models]
    end

    %% User Interface Connections
    User --> WebUI
    WebUI --> PromptEngine
    WebUI --> AnalysisCore
    WebUI --> StateManager

    %% Core Connections
    PromptEngine --> AnalysisCore
    AnalysisCore --> OpenAI

    %% Data Connections
    WebUI --> LocalData
    WebUI --> DemoCase
    WebUI --> ResultsDB
    Airtable --> LocalData

    %% Results Flow
    AnalysisCore --> StateManager
    StateManager --> ResultsDB

    classDef ui fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef core fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class User,WebUI ui
    class PromptEngine,AnalysisCore,StateManager core
    class LocalData,DemoCase,ResultsDB,Airtable data
    class OpenAI external
```

## Complete Analysis Workflow

This diagram shows the end-to-end analysis process with the new automated generator-based workflow:

```mermaid
flowchart TD
    Start([User Opens Application])

    subgraph "Input Phase"
        Citation[Enter Case Citation<br/>Required]
        InputSource{Choose Input Method}
        TextInput[Paste Court Decision Text<br/>Direct Input]
        PDFUpload[Upload PDF<br/>Automatic Extraction]
        DemoLoad[Use Demo Case<br/>BGE 132 III 285]
        EmailOpt[Optional Email<br/>Contact Info]
    end

    subgraph "Jurisdiction Detection"
        DetectJuris[Detect Legal System<br/>Civil Law/Common Law/India]
        DisplayJuris[Display Jurisdiction<br/>Results]
        ConfirmJuris[✓ User Confirms<br/>ONLY MANUAL STEP]
    end

    subgraph "Automated Analysis Workflow"
        StartGen[Start Generator Workflow<br/>analyze_case_workflow]

        subgraph "Step 1"
            ExtractCOL[Extract COL Sections<br/>Returns list of sections]
        end

        subgraph "Step 2"
            ClassifyTheme[Classify PIL Themes<br/>Against Taxonomy]
        end

        subgraph "Step 3 - Parallel Execution"
            Facts[Extract Relevant Facts]
            Provisions[Extract PIL Provisions]
            Issue[Identify COL Issue]
        end

        subgraph "Step 4 - Parallel Execution"
            Position[Extract Court Position]
            CommonLaw{Common Law?}
            ObiterDicta[Extract Obiter Dicta<br/>Common Law Only]
            DissentOps[Extract Dissenting Opinions<br/>Common Law Only]
        end

        subgraph "Step 5"
            Abstract[Generate Abstract<br/>Final Summary]
        end
    end

    subgraph "Review & Edit"
        ReviewAll[Review Complete Analysis<br/>Edit ALL Results]
        EditThemes[Edit Themes<br/>Multiselect]
        EditCOL[Edit COL Sections<br/>Textarea]
        EditOther[Edit Other Steps<br/>Facts, Issue, Position, etc.]
        SaveDB[Save to Database<br/>Optional PostgreSQL]
        Complete[Analysis Complete<br/>Display Summary]
    end

    End([User Completes Session])

    %% Flow connections
    Start --> Citation
    Citation --> EmailOpt
    EmailOpt --> InputSource

    InputSource --> TextInput
    InputSource --> PDFUpload
    InputSource --> DemoLoad

    TextInput --> DetectJuris
    PDFUpload --> DetectJuris
    DemoLoad --> DetectJuris

    DetectJuris --> DisplayJuris
    DisplayJuris --> ConfirmJuris
    ConfirmJuris --> StartGen

    StartGen --> ExtractCOL
    ExtractCOL --> ClassifyTheme
    ClassifyTheme --> Facts
    ClassifyTheme --> Provisions
    ClassifyTheme --> Issue

    Facts --> Position
    Provisions --> Position
    Issue --> Position

    Position --> CommonLaw
    CommonLaw -->|Yes| ObiterDicta
    CommonLaw -->|Yes| DissentOps
    CommonLaw -->|No| Abstract
    ObiterDicta --> Abstract
    DissentOps --> Abstract

    Abstract --> ReviewAll
    ReviewAll --> EditThemes
    ReviewAll --> EditCOL
    ReviewAll --> EditOther
    EditThemes --> SaveDB
    EditCOL --> SaveDB
    EditOther --> SaveDB
    SaveDB --> Complete
    Complete --> End

    classDef start fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef automated fill:#b3e5fc,stroke:#0277bd,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class Start,End start
    class Citation,EmailOpt,InputSource,TextInput,PDFUpload,DemoLoad input
    class DetectJuris,DisplayJuris process
    class ConfirmJuris decision
    class StartGen,ExtractCOL,ClassifyTheme,Facts,Provisions,Issue,Position,CommonLaw,ObiterDicta,DissentOps,Abstract automated
    class ReviewAll,EditThemes,EditCOL,EditOther,SaveDB,Complete output
```

## Detailed Component Workflows

### Jurisdiction Detection Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as UI Component
    participant Tool as Jurisdiction Detector
    participant Prompt as Prompt Selector
    participant LLM as OpenAI API
    participant State as Session State

    User->>UI: Click "Detect Jurisdiction"
    UI->>State: Get case citation & text
    State-->>UI: Return input data

    UI->>Tool: detect_jurisdiction(text, citation)
    Tool->>Prompt: Select detection prompt
    Prompt-->>Tool: System detection prompt

    Tool->>LLM: Analyze legal system
    Note over LLM: Identifies:<br/>- Legal system type<br/>- Specific jurisdiction<br/>- Confidence level
    LLM-->>Tool: Jurisdiction data

    Tool-->>UI: Display results
    UI->>User: Show jurisdiction with confirmation
    User->>UI: Confirm or override if needed

    UI->>State: Save jurisdiction
    State-->>UI: Confirmation
    UI-->>User: Ready for next step
```

### Streamlit Application Detailed Workflow

```mermaid
sequenceDiagram
    participant User
    participant App as Streamlit App
    participant Auth as Authentication
    participant StateManager as State Manager
    participant Components as UI Components
    participant Tools as Analysis Tools
    participant LLM as LLM Service
    participant DB as Database

    User->>App: Access web application
    App->>Auth: Initialize authentication
    Auth->>User: Present login (optional)
    User->>Auth: Provide credentials
    Auth-->>App: Authentication complete

    App->>StateManager: Initialize session state
    StateManager-->>App: State ready

    App->>User: Display case input interface
    User->>Components: Enter case citation
    User->>Components: Provide court decision text
    Components->>StateManager: Update state with input

    User->>App: Initiate jurisdiction detection
    App->>Tools: Detect jurisdiction
    Tools->>LLM: Analyze legal system
    LLM-->>Tools: Jurisdiction information
    Tools-->>Components: Display jurisdiction results
    User->>Components: Confirm jurisdiction

    Components->>Tools: Extract COL section
    Tools->>LLM: Identify COL sections
    LLM-->>Tools: COL section candidates
    Tools-->>Components: Display COL sections
    User->>Components: Edit COL section if needed
    Components->>StateManager: Update COL state

    Components->>Tools: Classify PIL theme
    Tools->>LLM: Analyze legal themes
    LLM-->>Tools: Theme classifications
    Tools-->>Components: Display themes
    User->>Components: Edit themes if needed
    Components->>StateManager: Update theme state

    Components->>Tools: Run complete analysis (parallel)
    Note over Tools,LLM: Step 3 parallel:<br/>Facts + PIL Provisions + COL Issue<br/>Step 4 parallel:<br/>Court Position + Obiter/Dissent
    Tools->>LLM: Extract all analysis components
    LLM-->>Tools: Complete analysis results
    Tools-->>Components: Display full analysis for editing

    User->>Components: Review and edit all results
    User->>Components: Submit final analysis

    Components->>DB: Save analysis results
    DB-->>Components: Confirm save
    Components-->>User: Analysis complete with save confirmation
```

### COL Extraction Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Workflow Component
    participant Generator as Case Analyzer (Generator)
    participant Tool as COL Extractor
    participant Prompt as Prompt Library
    participant LLM as OpenAI API
    participant State as Session State

    User->>UI: Confirm jurisdiction
    UI->>Generator: Start analyze_case_workflow()

    Generator->>Tool: extract_col_section(text, legal_system, jurisdiction)
    Tool->>Prompt: Get jurisdiction-specific prompt
    Prompt-->>Tool: COL extraction prompt

    Tool->>LLM: Extract COL sections
    Note over LLM: Identifies relevant<br/>Choice of Law sections<br/>Returns list of sections
    LLM-->>Tool: col_sections: list[str]

    Tool-->>Generator: Yield ColSectionOutput
    Generator-->>UI: Yield result object
    UI->>State: Save col_sections list
    UI->>User: Display progress

    Note over Generator,UI: Continues with themes,<br/>parallel analysis steps
```

### Theme Classification Workflow

```mermaid
sequenceDiagram
    participant Generator as Case Analyzer (Generator)
    participant Tool as Themes Classifier
    participant Data as Data Loader
    participant LLM as OpenAI API
    participant UI as Workflow Component
    participant State as Session State

    Note over Generator: After COL extraction
    Generator->>Data: Load valid themes
    Data-->>Generator: Theme taxonomy (themes.csv)

    Generator->>Tool: theme_classification_node(text, col_section, legal_system, jurisdiction)
    Tool->>LLM: Classify against PIL taxonomy
    Note over LLM: Categorizes case<br/>against predefined<br/>PIL themes
    LLM-->>Tool: Theme classifications

    Tool-->>Generator: Yield ThemeClassificationOutput
    Generator-->>UI: Yield result object
    UI->>State: Save themes
    UI->>User: Display progress

    Note over Generator,UI: Continues with parallel<br/>facts, provisions, COL issue
```

## Data Processing Patterns

### Input Data Transformation

```mermaid
flowchart LR
    subgraph "Raw Input"
        ManualText[Manual Text Input]
        PDFInput[PDF Upload]
        DemoCase[Demo Case Data]
        CSVData[Local CSV Files<br/>themes.csv]
    end

    subgraph "Processing Layer"
        PDFExtractor[PDF Text Extractor<br/>pymupdf4llm]
        TextCleaner[Text Cleaner<br/>Normalize Format]
        DataLoader[Data Loader<br/>CSV Parser]
        StateInit[State Initializer<br/>Session Setup]
    end

    subgraph "Structured Data"
        CleanText[Cleaned Text<br/>Analysis Ready]
        ThemeData[Theme Taxonomy<br/>Structured]
        CaseContext[Case Context<br/>With Metadata]
        SessionState[Session State<br/>Application Context]
    end

    ManualText --> TextCleaner
    PDFInput --> PDFExtractor
    DemoCase --> TextCleaner
    CSVData --> DataLoader
    PDFExtractor --> CleanText
    DataLoader --> ThemeData

    TextCleaner --> CleanText
    CleanText --> CaseContext
    ThemeData --> CaseContext
    CaseContext --> StateInit
    StateInit --> SessionState

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e9,stroke:#388e3c

    class ManualText,PDFInput,DemoCase,CSVData input
    class PDFExtractor,TextCleaner,DataLoader,StateInit process
    class CleanText,ThemeData,CaseContext,SessionState output
```

### Result Generation and Storage Pipeline

```mermaid
flowchart TD
    subgraph "Analysis Results"
        Jurisdiction[Jurisdiction Detection<br/>Legal System]
        COLSection[COL Section<br/>Legal Text Extract]
        Themes[PIL Themes<br/>Classification]
        PILProvisions[PIL Provisions<br/>Legal Rules]
        Abstract[Abstract<br/>Case Summary]
        Facts[Relevant Facts<br/>Factual Background]
        Issue[COL Issue<br/>Legal Question]
        Position[Court Position<br/>Legal Ruling]
    end

    subgraph "User Validation"
        ConfirmJuris[Confirm Jurisdiction]
        EditCOL[Edit COL Section]
        EditThemes[Edit Themes]
        FinalEdit[Final Edit All Results]
    end

    subgraph "Result Processing"
        Aggregator[Result Aggregator<br/>Combine All Components]
        Formatter[Result Formatter<br/>Structure Output]
    end

    subgraph "Storage Options"
        SessionOnly[Session State Only<br/>Temporary]
        DBSave[Database Save<br/>PostgreSQL]
    end

    Jurisdiction --> ConfirmJuris
    COLSection --> EditCOL
    Themes --> EditThemes
    PILProvisions --> FinalEdit
    Abstract --> FinalEdit
    Facts --> FinalEdit
    Issue --> FinalEdit
    Position --> FinalEdit

    ConfirmJuris --> Aggregator
    EditCOL --> Aggregator
    EditThemes --> Aggregator
    FinalEdit --> Aggregator

    Aggregator --> Formatter
    Formatter --> SessionOnly
    Formatter --> DBSave

    classDef analysis fill:#e3f2fd,stroke:#1976d2
    classDef validation fill:#fff3e0,stroke:#f57c00
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef storage fill:#e8f5e9,stroke:#388e3c

    class Jurisdiction,COLSection,Themes,PILProvisions,Abstract,Facts,Issue,Position analysis
    class ConfirmJuris,EditCOL,EditThemes,FinalEdit validation
    class Aggregator,Formatter process
    class SessionOnly,DBSave storage
```

## Summary

This workflow documentation provides a comprehensive overview of the CoLD Case Analyzer's operational processes:

- **Main Workflow**: Generator-based automated analysis from jurisdiction confirmation to completion
- **Component Workflows**: Jurisdiction detection, COL extraction, and theme classification
- **Data Processing**: Input transformation and result storage patterns

### Current Implementation

**Generator-Based Workflow:**

- All analysis steps after jurisdiction confirmation are automated
- Uses `analyze_case_workflow()` generator function that yields result objects
- User confirms jurisdiction only; all other steps run automatically

**Parallel Execution:**

- Step 3: Facts + PIL Provisions + COL Issue (3 parallel operations)
- Step 4: Court Position + Obiter Dicta + Dissenting Opinions (up to 3 parallel operations for Common Law)

**Parameter Naming:**

- `legal_system`: Type of legal system (e.g., "Civil-law jurisdiction", "Common-law jurisdiction")
- `jurisdiction`: Specific jurisdiction (e.g., "Switzerland", "United States", "India")
- `themes`: Classified PIL themes

**ColSectionOutput Model:**

- Returns `col_sections: list[str]` supporting multiple Choice of Law sections
- Sections are joined with double newlines for processing

**Workflow Steps:**

1. **COL Section Extraction**: Yields `ColSectionOutput` with list of sections
2. **Theme Classification**: Yields `ThemeClassificationOutput` with themes list
3. **Parallel Analysis Step 1**: Yields `RelevantFactsOutput`, `PILProvisionsOutput`, and `ColIssueOutput` in parallel
4. **Parallel Analysis Step 2**: Yields `CourtsPositionOutput`, and for Common Law: `ObiterDictaOutput` and `DissentingOpinionsOutput` in parallel
5. **Abstract**: Yields `AbstractOutput` synthesizing all previous steps

**Final Editing Phase:**

- User can edit all results including themes, COL sections, and all analysis steps
- Single comprehensive review before saving
