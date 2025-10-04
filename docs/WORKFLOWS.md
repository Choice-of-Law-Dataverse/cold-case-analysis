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
    
    subgraph "LATAM Module"
        Airtable[(Airtable<br/>PDF Source)]
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

This diagram shows the end-to-end analysis process from input to final results:

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
        ScoreJuris[User Scores Result<br/>0-100]
        EditJuris[Edit if Needed<br/>Manual Correction]
    end
    
    subgraph "COL Section Extraction"
        ExtractCOL[Extract COL Sections<br/>Identify Relevant Text]
        DisplayCOL[Display Extracted<br/>Sections]
        ScoreCOL[User Scores Extraction<br/>0-100]
        FeedbackCOL[Provide Feedback<br/>Edit/Refine]
    end
    
    subgraph "Theme Classification"
        ClassifyTheme[Classify PIL Themes<br/>Against Taxonomy]
        DisplayThemes[Display Classified<br/>Themes]
        ScoreThemes[User Scores Themes<br/>0-100]
        EditThemes[Edit Theme List<br/>Manual Adjustment]
    end
    
    subgraph "PIL Provisions"
        ExtractPIL[Extract PIL Provisions<br/>Legal Rules]
        DisplayPIL[Display Provisions]
        ScorePIL[User Scores<br/>0-100]
    end
    
    subgraph "Detailed Analysis Steps"
        Abstract[1. Extract Abstract<br/>Case Summary]
        Facts[2. Extract Relevant Facts<br/>Factual Background]
        Provisions[3. Identify PIL Provisions<br/>Applicable Rules]
        Issue[4. Identify COL Issue<br/>Legal Question]
        Position[5. Extract Court Position<br/>Court's Reasoning]
    end
    
    subgraph "Review & Save"
        ReviewAll[Review Complete Analysis<br/>All Components]
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
    DisplayJuris --> ScoreJuris
    ScoreJuris --> EditJuris
    EditJuris --> ExtractCOL
    
    ExtractCOL --> DisplayCOL
    DisplayCOL --> ScoreCOL
    ScoreCOL --> FeedbackCOL
    FeedbackCOL --> ClassifyTheme
    
    ClassifyTheme --> DisplayThemes
    DisplayThemes --> ScoreThemes
    ScoreThemes --> EditThemes
    EditThemes --> ExtractPIL
    
    ExtractPIL --> DisplayPIL
    DisplayPIL --> ScorePIL
    ScorePIL --> Abstract
    
    Abstract --> Facts
    Facts --> Provisions
    Provisions --> Issue
    Issue --> Position
    
    Position --> ReviewAll
    ReviewAll --> SaveDB
    SaveDB --> Complete
    Complete --> End

    classDef start fill:#e8f5e9,stroke:#388e3c,stroke-width:3px
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#c2185b,stroke-width:2px

    class Start,End start
    class Citation,EmailOpt,InputSource,TextInput,PDFUpload,DemoLoad input
    class DetectJuris,DisplayJuris,ExtractCOL,DisplayCOL,ClassifyTheme,DisplayThemes,ExtractPIL,DisplayPIL,Abstract,Facts,Provisions,Issue,Position process
    class ScoreJuris,EditJuris,ScoreCOL,FeedbackCOL,ScoreThemes,EditThemes,ScorePIL decision
    class ReviewAll,SaveDB,Complete output
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
    UI->>User: Show jurisdiction with score field
    User->>UI: Score result (0-100)
    User->>UI: Edit if needed
    
    UI->>State: Save jurisdiction & score
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
    User->>Components: Provide feedback on COL sections
    Components->>StateManager: Update COL state
    
    Components->>Tools: Classify PIL theme
    Tools->>LLM: Analyze legal themes
    LLM-->>Tools: Theme classifications
    Tools-->>Components: Display themes
    User->>Components: Score and validate themes
    Components->>StateManager: Update theme state
    
    Components->>Tools: Run complete analysis
    Tools->>LLM: Extract all analysis components
    LLM-->>Tools: Complete analysis results
    Tools-->>Components: Display full analysis
    User->>Components: Review and provide feedback
    
    Components->>DB: Save analysis results
    DB-->>Components: Confirm save
    Components-->>User: Analysis complete with save confirmation
```

### COL Extraction Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as COL Processor
    participant Tool as COL Extractor
    participant Prompt as Prompt Library
    participant LLM as OpenAI API
    participant State as Session State

    User->>UI: Proceed to COL extraction
    UI->>State: Get jurisdiction & text
    State-->>UI: Return context
    
    UI->>Tool: extract_col_sections(text, jurisdiction)
    Tool->>Prompt: Get jurisdiction-specific prompt
    Prompt-->>Tool: COL extraction prompt
    
    Tool->>LLM: Extract COL sections
    Note over LLM: Identifies relevant<br/>Choice of Law sections<br/>from court decision
    LLM-->>Tool: COL section list
    
    Tool-->>UI: Display extracted sections
    UI->>User: Show COL sections
    User->>UI: Score extraction (0-100)
    User->>UI: Provide feedback/edit
    
    UI->>State: Save COL sections & feedback
    State-->>UI: Confirmation
    UI-->>User: Ready for theme classification
```

### Theme Classification Workflow

```mermaid
sequenceDiagram
    participant User
    participant UI as Theme Classifier
    participant Data as Data Loader
    participant Tool as Themes Classifier
    participant LLM as OpenAI API
    participant State as Session State

    User->>UI: Proceed to theme classification
    UI->>Data: Load valid themes
    Data-->>UI: Theme taxonomy (themes.csv)
    
    UI->>State: Get COL sections
    State-->>UI: Return COL data
    
    UI->>Tool: classify_themes(col_sections, themes)
    Tool->>LLM: Classify against PIL taxonomy
    Note over LLM: Categorizes case<br/>against predefined<br/>PIL themes
    LLM-->>Tool: Theme classifications
    
    Tool-->>UI: Display classified themes
    UI->>User: Show themes with scores
    User->>UI: Score themes (0-100)
    User->>UI: Edit theme selections
    
    UI->>State: Save themes & scores
    State-->>UI: Confirmation
    UI-->>User: Ready for detailed analysis
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
        ScoreJuris[Score Jurisdiction]
        ScoreCOL[Score COL Sections]
        ScoreThemes[Score Themes]
        ScorePIL[Score PIL Provisions]
        ScoreAnalysis[Score Each Analysis Step]
    end
    
    subgraph "Result Processing"
        Aggregator[Result Aggregator<br/>Combine All Components]
        Formatter[Result Formatter<br/>Structure Output]
    end
    
    subgraph "Storage Options"
        SessionOnly[Session State Only<br/>Temporary]
        DBSave[Database Save<br/>PostgreSQL]
    end
    
    Jurisdiction --> ScoreJuris
    COLSection --> ScoreCOL
    Themes --> ScoreThemes
    PILProvisions --> ScorePIL
    Abstract --> ScoreAnalysis
    Facts --> ScoreAnalysis
    Issue --> ScoreAnalysis
    Position --> ScoreAnalysis
    
    ScoreJuris --> Aggregator
    ScoreCOL --> Aggregator
    ScoreThemes --> Aggregator
    ScorePIL --> Aggregator
    ScoreAnalysis --> Aggregator
    
    Aggregator --> Formatter
    Formatter --> SessionOnly
    Formatter --> DBSave
    
    classDef analysis fill:#e3f2fd,stroke:#1976d2
    classDef validation fill:#fff3e0,stroke:#f57c00
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef storage fill:#e8f5e9,stroke:#388e3c
    
    class Jurisdiction,COLSection,Themes,PILProvisions,Abstract,Facts,Issue,Position analysis
    class ScoreJuris,ScoreCOL,ScoreThemes,ScorePIL,ScoreAnalysis validation
    class Aggregator,Formatter process
    class SessionOnly,DBSave storage
```

## Summary

This workflow documentation provides a comprehensive overview of the CoLD Case Analyzer's operational processes:

- **Main Workflow**: Step-by-step user-guided analysis from input to completion
- **Component Workflows**: Detailed flows for jurisdiction detection, COL extraction, and theme classification
