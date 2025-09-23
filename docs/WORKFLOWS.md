# Cold Case Analysis - System Workflow Documentation

This document provides detailed workflow diagrams and data flow patterns for the Cold Case Analysis system.

## High-Level System Interaction

```mermaid
graph TB
    subgraph "User Interfaces"
        CLI[Command Line Interface<br/>Batch Processing]
        WebUI[Web Interface<br/>Interactive Analysis]
        GraphAPI[LangGraph API<br/>Advanced Workflows]
    end
    
    subgraph "Core Analysis Engine"
        LLMRouter[LLM Router<br/>Model Selection]
        AnalysisCore[Analysis Core<br/>Case Processing]
        PromptEngine[Prompt Engine<br/>Template Management]
    end
    
    subgraph "Data Layer"
        LocalData[(Local Files<br/>Excel/CSV)]
        RemoteData[(Airtable<br/>Cloud Data)]
        ResultsDB[(PostgreSQL<br/>Results Storage)]
        GroundTruth[(Ground Truth<br/>Evaluation Data)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT Models]
        LlamaAPI[Llama API<br/>Open Source Models]
    end
    
    %% User Interface Connections
    CLI --> LLMRouter
    WebUI --> LLMRouter
    GraphAPI --> LLMRouter
    
    %% Core Engine Connections
    LLMRouter --> AnalysisCore
    AnalysisCore --> PromptEngine
    
    %% Data Connections
    CLI --> LocalData
    CLI --> RemoteData
    WebUI --> LocalData
    WebUI --> ResultsDB
    CLI --> GroundTruth
    
    %% External Service Connections
    LLMRouter --> OpenAI
    LLMRouter --> LlamaAPI
    
    %% Results Flow
    AnalysisCore --> ResultsDB
    AnalysisCore --> LocalData

    classDef ui fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef core fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#f57c00,stroke-width:2px

    class CLI,WebUI,GraphAPI ui
    class LLMRouter,AnalysisCore,PromptEngine core
    class LocalData,RemoteData,ResultsDB,GroundTruth data
    class OpenAI,LlamaAPI external
```

## Complete Analysis Workflow

This diagram shows the end-to-end analysis process from input to final results:

```mermaid
flowchart TD
    Start([User Initiates Analysis])
    
    subgraph "Input Phase"
        DataSource{Select Data Source}
        LocalInput[Load Local Cases<br/>cases.xlsx]
        AirtableInput[Fetch Airtable Data<br/>Remote Cases]
        ManualInput[Manual Text Input<br/>Single Case]
        ModelSelect[Select LLM Model<br/>GPT-4o/Mini/Llama]
    end
    
    subgraph "Pre-Processing"
        ValidateInput[Validate Input Data<br/>Required Fields Check]
        JurisdictionDetect[Detect Jurisdiction<br/>Legal System Identification]
        PrepareContext[Prepare Analysis Context<br/>Load Concepts & Prompts]
    end
    
    subgraph "Core Analysis Loop"
        ExtractCOL[Extract Choice of Law Section<br/>Key Legal Text Identification]
        ValidateCOL{User Validates COL Section}
        ClassifyTheme[Classify PIL Theme<br/>Legal Topic Classification]
        ValidateTheme{User Validates Theme}
        
        subgraph "Detailed Analysis"
            ExtractAbstract[Extract Abstract<br/>Case Summary]
            ExtractFacts[Extract Relevant Facts<br/>Factual Background]
            ExtractProvisions[Extract PIL Provisions<br/>Legal Rules]
            IdentifyIssue[Identify COL Issue<br/>Legal Question]
            ExtractPosition[Extract Court Position<br/>Legal Ruling]
        end
    end
    
    subgraph "Post-Processing"
        CompileResults[Compile Analysis Results<br/>Structured Output]
        FormatOutput[Format Final Output<br/>User-Friendly Display]
        ValidateResults{User Validates Results}
        SaveResults[Save Results<br/>Database/File Storage]
        GenerateReport[Generate Analysis Report<br/>Summary & Insights]
    end
    
    subgraph "Evaluation & Feedback"
        CompareGroundTruth[Compare with Ground Truth<br/>Quality Assessment]
        CollectFeedback[Collect User Feedback<br/>Improvement Data]
        UpdateModel[Update Model Performance<br/>Learning Integration]
    end
    
    End([Analysis Complete])
    
    %% Flow connections
    Start --> DataSource
    DataSource --> LocalInput
    DataSource --> AirtableInput
    DataSource --> ManualInput
    
    LocalInput --> ModelSelect
    AirtableInput --> ModelSelect
    ManualInput --> ModelSelect
    
    ModelSelect --> ValidateInput
    ValidateInput --> JurisdictionDetect
    JurisdictionDetect --> PrepareContext
    PrepareContext --> ExtractCOL
    
    ExtractCOL --> ValidateCOL
    ValidateCOL -->|Approved| ClassifyTheme
    ValidateCOL -->|Rejected| ExtractCOL
    
    ClassifyTheme --> ValidateTheme
    ValidateTheme -->|Approved| ExtractAbstract
    ValidateTheme -->|Rejected| ClassifyTheme
    
    ExtractAbstract --> ExtractFacts
    ExtractFacts --> ExtractProvisions
    ExtractProvisions --> IdentifyIssue
    IdentifyIssue --> ExtractPosition
    
    ExtractPosition --> CompileResults
    CompileResults --> FormatOutput
    FormatOutput --> ValidateResults
    
    ValidateResults -->|Approved| SaveResults
    ValidateResults -->|Refinement Needed| ExtractAbstract
    
    SaveResults --> GenerateReport
    GenerateReport --> CompareGroundTruth
    CompareGroundTruth --> CollectFeedback
    CollectFeedback --> UpdateModel
    UpdateModel --> End

    classDef start fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef input fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef output fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef end fill:#e8f5e8,stroke:#388e3c,stroke-width:3px

    class Start,End start
    class DataSource,LocalInput,AirtableInput,ManualInput,ModelSelect input
    class ValidateInput,JurisdictionDetect,PrepareContext,ExtractCOL,ClassifyTheme,ExtractAbstract,ExtractFacts,ExtractProvisions,IdentifyIssue,ExtractPosition,CompileResults,FormatOutput process
    class ValidateCOL,ValidateTheme,ValidateResults decision
    class SaveResults,GenerateReport,CompareGroundTruth,CollectFeedback,UpdateModel output
```

## Application-Specific Workflows

### CLI Application Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI Main
    participant DataHandler as Data Handler
    participant CaseAnalyzer as Case Analyzer
    participant LLM as LLM Service
    participant Evaluator as Result Evaluator
    participant Storage as File Storage

    User->>CLI: python main.py
    CLI->>User: Select data source
    User->>CLI: Choose "Own data" or "Airtable"
    CLI->>User: Select model
    User->>CLI: Choose "gpt-4o", "gpt-4o-mini", or "llama3.1"
    
    CLI->>DataHandler: Load cases and concepts
    DataHandler->>Storage: Read cases.xlsx, concepts.xlsx
    Storage-->>DataHandler: Return case data
    DataHandler-->>CLI: Provide structured data
    
    loop For each case in dataset
        CLI->>CaseAnalyzer: Create analyzer instance
        CaseAnalyzer->>LLM: Extract COL section
        LLM-->>CaseAnalyzer: COL section text
        
        CaseAnalyzer->>LLM: Extract abstract
        LLM-->>CaseAnalyzer: Abstract text
        
        CaseAnalyzer->>LLM: Extract relevant facts
        LLM-->>CaseAnalyzer: Facts summary
        
        CaseAnalyzer->>LLM: Extract PIL provisions
        LLM-->>CaseAnalyzer: Legal provisions list
        
        CaseAnalyzer->>LLM: Classify theme and identify issue
        LLM-->>CaseAnalyzer: Theme classification and issue
        
        CaseAnalyzer->>LLM: Extract court position
        LLM-->>CaseAnalyzer: Court's position
        
        CaseAnalyzer-->>CLI: Complete analysis results
    end
    
    CLI->>Storage: Save results to CSV with timestamp
    CLI->>User: Offer evaluation option
    
    alt User chooses evaluation
        User->>CLI: Yes, evaluate
        CLI->>Evaluator: Compare with ground truth
        Evaluator->>Storage: Load ground truth data
        Storage-->>Evaluator: Ground truth results
        Evaluator-->>User: Display evaluation metrics
    else User skips evaluation
        User->>CLI: No evaluation
        CLI-->>User: Analysis complete
    end
```

### Streamlit Application Workflow

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

### LangGraph Engine Workflow

```mermaid
stateDiagram-v2
    [*] --> TextInput : Court decision text
    
    TextInput --> COLExtraction : Initialize analysis
    COLExtraction --> COLValidation : Present COL sections
    
    COLValidation --> ThemeClassification : User approves
    COLValidation --> COLExtraction : User requests changes
    
    ThemeClassification --> ThemeValidation : Present themes
    ThemeValidation --> SequentialAnalysis : User approves
    ThemeValidation --> ThemeClassification : User requests changes
    
    SequentialAnalysis --> AbstractExtraction : Begin detailed analysis
    AbstractExtraction --> FactsExtraction
    FactsExtraction --> ProvisionsExtraction
    ProvisionsExtraction --> IssueIdentification
    IssueIdentification --> PositionExtraction
    PositionExtraction --> ResultFormatting
    
    ResultFormatting --> FinalReview : Present complete analysis
    FinalReview --> [*] : User approves
    FinalReview --> ResultFormatting : User requests refinement
    
    note right of COLValidation
        Human-in-the-loop validation
        User can provide specific feedback
        System refines extraction based on input
    end note
    
    note right of ThemeValidation
        Theme classification validation
        User selects appropriate themes
        System adjusts based on selection
    end note
    
    note right of FinalReview
        Complete analysis review
        User can request improvements
        System refines specific sections
    end note
```

## Data Processing Patterns

### Input Data Transformation

```mermaid
flowchart LR
    subgraph "Raw Input"
        RawText[Court Decision Text<br/>Unstructured]
        ExcelData[Excel Files<br/>cases.xlsx, concepts.xlsx]
        PDFInput[PDF Documents<br/>Uploaded Files]
        AirtableData[Airtable Records<br/>Structured Data]
    end
    
    subgraph "Processing Layer"
        TextCleaner[Text Cleaner<br/>Remove Artifacts]
        PDFExtractor[PDF Extractor<br/>Text Extraction]
        DataValidator[Data Validator<br/>Schema Check]
        Normalizer[Data Normalizer<br/>Format Standardization]
    end
    
    subgraph "Structured Data"
        CleanText[Clean Text<br/>Analysis Ready]
        CaseData[Case Data<br/>Structured Format]
        ConceptData[Concept Data<br/>Classification Schema]
        SessionState[Session State<br/>Application Context]
    end
    
    RawText --> TextCleaner
    PDFInput --> PDFExtractor
    ExcelData --> DataValidator
    AirtableData --> DataValidator
    
    TextCleaner --> CleanText
    PDFExtractor --> CleanText
    DataValidator --> Normalizer
    
    Normalizer --> CaseData
    Normalizer --> ConceptData
    CleanText --> SessionState
    CaseData --> SessionState
    ConceptData --> SessionState

    classDef input fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e8,stroke:#388e3c

    class RawText,ExcelData,PDFInput,AirtableData input
    class TextCleaner,PDFExtractor,DataValidator,Normalizer process
    class CleanText,CaseData,ConceptData,SessionState output
```

### Result Generation Pipeline

```mermaid
flowchart TD
    subgraph "Analysis Results"
        COLSection[COL Section<br/>Legal Text Extract]
        Abstract[Abstract<br/>Case Summary]
        Facts[Relevant Facts<br/>Factual Background]
        Provisions[PIL Provisions<br/>Legal Rules]
        Theme[PIL Theme<br/>Classification]
        Issue[COL Issue<br/>Legal Question]
        Position[Court Position<br/>Legal Ruling]
    end
    
    subgraph "Result Processing"
        Validator[Result Validator<br/>Quality Check]
        Formatter[Result Formatter<br/>Output Structuring]
        Aggregator[Result Aggregator<br/>Combine Components]
    end
    
    subgraph "Output Formats"
        JSONOutput[JSON Format<br/>Structured Data]
        CSVOutput[CSV Format<br/>Tabular Data]
        ReportOutput[Report Format<br/>Human Readable]
        DBRecord[Database Record<br/>Persistent Storage]
    end
    
    subgraph "Quality Assurance"
        GroundTruthCheck[Ground Truth Comparison<br/>Accuracy Assessment]
        UserFeedback[User Feedback<br/>Quality Evaluation]
        MetricsCalculation[Performance Metrics<br/>System Evaluation]
    end
    
    COLSection --> Validator
    Abstract --> Validator
    Facts --> Validator
    Provisions --> Validator
    Theme --> Validator
    Issue --> Validator
    Position --> Validator
    
    Validator --> Formatter
    Formatter --> Aggregator
    
    Aggregator --> JSONOutput
    Aggregator --> CSVOutput
    Aggregator --> ReportOutput
    Aggregator --> DBRecord
    
    JSONOutput --> GroundTruthCheck
    CSVOutput --> GroundTruthCheck
    DBRecord --> UserFeedback
    ReportOutput --> UserFeedback
    
    GroundTruthCheck --> MetricsCalculation
    UserFeedback --> MetricsCalculation

    classDef analysis fill:#e3f2fd,stroke:#1976d2
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#e8f5e8,stroke:#388e3c
    classDef quality fill:#fff3e0,stroke:#f57c00

    class COLSection,Abstract,Facts,Provisions,Theme,Issue,Position analysis
    class Validator,Formatter,Aggregator process
    class JSONOutput,CSVOutput,ReportOutput,DBRecord output
    class GroundTruthCheck,UserFeedback,MetricsCalculation quality
```

This workflow documentation provides detailed insights into how the Cold Case Analysis system processes data and manages user interactions across all three application interfaces.