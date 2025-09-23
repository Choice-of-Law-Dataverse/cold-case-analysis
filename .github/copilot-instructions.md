# Cold Case Analysis - Choice of Law Dataverse (CoLD)

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup
- Python 3.12.3 with pip package manager
- **NEVER CANCEL** build or install commands - they may take several minutes
- Bootstrap the repository:
  - `cp blueprint.env .env` - Create environment file from template
  - `pip install -r requirements.txt` - Install dependencies. Takes ~60 seconds. NEVER CANCEL. Set timeout to 180+ seconds.
  - For Streamlit app: `pip install pymupdf4llm psycopg2-binary` - Install missing dependencies (not in requirements.txt)

### Running Applications

#### 1. Main CLI Case Analyzer (cold_case_analyzer)
- **Entry point**: `python cold_case_analyzer/main.py`
- **Interactive tool**: Provides menu to select data source (Own data/Airtable) and model (gpt-4o, gpt-4o-mini, llama3.1)
- **Data requirements**: Requires `cold_case_analyzer/data/cases.xlsx` with pre-defined column format
- **API Key**: Requires OPENAI_API_KEY in .env file for LLM functionality
- **Processing time**: Analysis can take several minutes per case. NEVER CANCEL operations.

#### 2. Streamlit Web Application (cold_case_analyzer_agent/streamlit)
- **Entry point**: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
- **Working directory**: Must run from `cold_case_analyzer_agent/streamlit/`
- **URL**: http://localhost:8501
- **Demo data**: Click "Use Demo Case" to load BGE 132 III 285 Swiss court case for testing
- **Features**: 
  - Interactive case analysis workflow
  - Jurisdiction detection
  - Choice of Law section extraction
  - Legal theme classification
  - Step-by-step analysis with user feedback
- **Authentication**: Optional login system (credentials in USER_CREDENTIALS env var)
- **Dependencies**: Requires OPENAI_API_KEY, optional database connection (PostgreSQL)

#### 3. LangGraph Analysis Engine (cold_case_analyzer/cca_langgraph)
- **Entry point**: `python cold_case_analyzer/cca_langgraph/main.py`
- **Purpose**: Advanced workflow orchestration using LangGraph for court case analysis
- **Features**: Graph-based analysis with interrupts for user feedback
- **Models**: Uses gpt-4.1-nano model by default
- **Components**: 
  - Node-based workflow (jurisdiction detection, theme classification, etc.)
  - Interrupt handlers for human-in-the-loop analysis
  - Memory checkpointing for workflow state

### Docker Setup
- **Location**: `cold_case_analyzer_agent/streamlit/Dockerfile`
- **Known issue**: Docker build may fail due to SSL certificate issues in some environments
- **Workaround**: Use native Python environment instead of Docker for development
- **Entry script**: `docker-entrypoint.sh` generates secrets.toml and runs Streamlit

### Testing
- **Test location**: `cold_case_analyzer_agent/streamlit/tests/`
- **Run tests**: `pytest tests/ -v --tb=short`
- **Requirements**: 
  - Set OPENAI_API_KEY=test_key in .env file
  - Some tests may have import issues due to module path dependencies
  - Tests exist for prompt logic, workflow integration, and system functionality
- **Test timeout**: Set timeout to 300+ seconds for test runs. NEVER CANCEL.

## Validation

### Always perform these validation steps after making changes:

1. **Basic Python environment**:
   - `python --version` (should show Python 3.12.3)
   - `pip install -r requirements.txt` 
   - `python -c "import streamlit; print('✓ Streamlit works')"`

2. **CLI Case Analyzer**:
   - `cd /path/to/repo && python cold_case_analyzer/main.py`
   - Verify interactive menu appears (select Own data → gpt-4o for basic test)
   - Use Ctrl+C to exit if no data available

3. **LangGraph Analysis Engine**:
   - `cd cold_case_analyzer/cca_langgraph && python main.py`
   - Verify graph-based workflow interface
   - Requires OPENAI_API_KEY for LLM functionality
   - Uses gpt-4.1-nano model by default

4. **Streamlit Application Manual Validation**:
   - `cd cold_case_analyzer_agent/streamlit`
   - `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`
   - Navigate to http://localhost:8501
   - Click "Use Demo Case" button
   - Verify BGE 132 III 285 case data loads in citation and text fields
   - Click "Detect Jurisdiction" to test basic workflow
   - **Expected**: App loads Swiss Federal Supreme Court case with jurisdiction detection interface

5. **Dependencies check**:
   ```bash
   python -c "import pymupdf4llm, psycopg2, langgraph; print('✓ All deps available')"
   ```

## Common Tasks

### Repository Structure
```
cold-case-analysis/
├── README.md                           # Main project documentation
├── requirements.txt                    # Python dependencies for CLI
├── blueprint.env                       # Environment template
├── cold_case_analyzer/                 # Main CLI application
│   ├── main.py                         # CLI entry point
│   ├── cca_langgraph/                  # LangGraph workflow engine
│   │   ├── main.py                     # LangGraph entry point
│   │   ├── nodes/                      # Workflow nodes
│   │   └── tools/                      # Analysis tools
│   ├── data/                           # Input data (cases.xlsx, concepts.xlsx)
│   ├── case_analyzer/                  # Core analysis logic
│   └── evaluator/                      # Result evaluation tools
├── cold_case_analyzer_agent/           # Web application
│   ├── streamlit/                      # Streamlit web app
│   │   ├── app.py                      # Web app entry point
│   │   ├── requirements.txt            # Web app dependencies
│   │   ├── tests/                      # Test suite
│   │   ├── components/                 # UI components
│   │   ├── utils/                      # Utility functions
│   │   └── tools/                      # Analysis tools
│   ├── Dockerfile                      # Empty/placeholder
│   └── docker-compose.yaml            # Empty/placeholder
└── docs/                               # Additional documentation
```

### Key Files to Check When Making Changes
- **Config files**: `cold_case_analyzer/config.py`, `cold_case_analyzer_agent/streamlit/config.py`
- **Environment**: `.env` (created from blueprint.env)
- **Main entry points**: `cold_case_analyzer/main.py`, `cold_case_analyzer/cca_langgraph/main.py`, `cold_case_analyzer_agent/streamlit/app.py`
- **Dependencies**: `requirements.txt` (root), `cold_case_analyzer_agent/streamlit/requirements.txt`

### Data Formats
- **Input cases**: Excel format (`cold_case_analyzer/data/cases.xlsx`) with columns: ID, Original text, Quote
- **Concepts**: Excel format (`cold_case_analyzer/data/concepts.xlsx`) for legal theme classification
- **Ground truth**: CSV format for evaluation comparisons

### API Integration
- **OpenAI**: Primary LLM provider (GPT-4o, GPT-4o-mini models)
- **Llama API**: Alternative LLM provider (llama3.1 model) 
- **Airtable**: Optional data source (requires AIRTABLE_API_KEY, AIRTABLE_BASE_ID)
- **PostgreSQL**: Optional database for Streamlit app results

### Performance Notes
- **CLI analysis**: Each court case takes several minutes to process
- **Streamlit startup**: App takes ~5-10 seconds to fully load
- **Install time**: Main requirements.txt takes ~60 seconds, Streamlit requirements may timeout due to large dependencies
- **Memory usage**: LLM processing can be memory intensive for longer court decisions

## Troubleshooting

### Common Issues
1. **ModuleNotFoundError for 'pymupdf4llm'**: Install with `pip install pymupdf4llm`
2. **ModuleNotFoundError for 'psycopg2'**: Install with `pip install psycopg2-binary`
3. **OPENAI_API_KEY not set**: Copy blueprint.env to .env and set your API key
4. **Streamlit won't start**: Check you're in the correct directory (`cold_case_analyzer_agent/streamlit/`)
5. **Docker build fails**: Use native Python environment due to SSL certificate issues
6. **Test import errors**: Tests have module path dependencies, run from correct directory
7. **Interactive CLI hangs**: CLI tools are interactive, use appropriate timeout settings

### Expected Timeouts
- **pip install -r requirements.txt**: 180+ seconds (NEVER CANCEL)
- **Streamlit app startup**: 30+ seconds (NEVER CANCEL)
- **Case analysis**: 300+ seconds per case (NEVER CANCEL)
- **Test execution**: 300+ seconds (NEVER CANCEL)

### Environment Variables Required
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

# Optional for authentication
USER_CREDENTIALS={"username":"password"}

# Optional for database
SQL_CONN_STRING=postgresql://user:pass@host:port/db
```