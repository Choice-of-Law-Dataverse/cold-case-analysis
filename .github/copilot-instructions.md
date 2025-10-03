# CoLD Case Analyzer - Choice of Law Dataverse

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup
- Python 3.12+ with pip or uv package manager
- **NEVER CANCEL** build or install commands - they may take several minutes
- Bootstrap the repository:
  - `cp .env.example .env` - Create environment file from template
  - `pip install streamlit langchain-core langchain-openai pandas pymupdf4llm psycopg2-binary python-dotenv requests` - Install dependencies. Takes ~60 seconds. NEVER CANCEL. Set timeout to 180+ seconds.
  - Or use `uv sync` for faster installation with the uv package manager

### Running the Application

#### Streamlit Web Application (src/)
- **Entry point**: `cd src && streamlit run app.py` OR `uv run streamlit run src/app.py`
- **Working directory**: Repository root or `src/` directory
- **URL**: http://localhost:8501
- **Demo data**: Click "Use Demo Case" to load BGE 132 III 285 Swiss court case for testing
- **Features**: 
  - Interactive case analysis workflow
  - Jurisdiction detection (Civil Law, Common Law, India)
  - Choice of Law section extraction
  - PIL theme classification
  - Step-by-step analysis with user feedback/scoring
  - Optional database persistence
- **Authentication**: Optional login system (credentials in USER_CREDENTIALS env var)
- **Dependencies**: Requires OPENAI_API_KEY, optional PostgreSQL database connection

### Docker Setup
- **Location**: `Dockerfile` (repository root)
- **Build**: `docker build -t cold-case-analyzer .`
- **Run**: `docker run -p 8501:8501 --env-file .env cold-case-analyzer`
- **Entry**: Docker starts Streamlit automatically on port 8501

### Testing
- **Test location**: `src/tests/`
- **Run tests**: `cd src && pytest tests/ -v --tb=short`
- **Requirements**: 
  - Set OPENAI_API_KEY=test_key in .env file
  - Tests exist for prompts, workflows, and system functionality
- **Test timeout**: Set timeout to 300+ seconds for test runs. NEVER CANCEL.

## Validation

### Always perform these validation steps after making changes:

1. **Basic Python environment**:
   - `python --version` (should show Python 3.12+)
   - `pip install streamlit langchain-core langchain-openai pandas pymupdf4llm psycopg2-binary python-dotenv requests`
   - `cd src && python -c "import streamlit; print('✓ Streamlit works')"`

2. **Streamlit Application**:
   - `cd src && streamlit run app.py` OR `uv run streamlit run src/app.py`
   - Open http://localhost:8501
   - Click "Use Demo Case" button
   - Verify BGE 132 III 285 case loads in citation and text fields
   - Click "Detect Jurisdiction" to test basic workflow
   - **Expected**: App loads Swiss Federal Supreme Court case with jurisdiction detection interface

3. **Component Imports**:
   ```bash
   cd src
   python -c "from components.input_handler import render_input_phase; print('✓ Components work')"
   python -c "from tools.case_analyzer import analyze_case; print('✓ Tools work')"
   python -c "from utils.state_manager import initialize_col_state; print('✓ Utils work')"
   ```

4. **Dependencies check**:
   ```bash
   python -c "import pymupdf4llm, psycopg2, langchain_openai; print('✓ All deps available')"
   ```

## Common Tasks

### Repository Structure
```
cold-case-analysis/
├── README.md                           # Main project documentation
├── pyproject.toml                      # Python project configuration
├── uv.lock                             # Dependency lock file
├── .env.example                        # Environment template
├── Dockerfile                          # Docker deployment
├── src/                                # Main application
│   ├── app.py                          # Streamlit entry point
│   ├── config.py                       # Configuration management
│   ├── components/                     # UI components
│   │   ├── auth.py                     # Authentication
│   │   ├── input_handler.py            # Input handling
│   │   ├── jurisdiction_detection.py   # Jurisdiction detection
│   │   ├── col_processor.py            # COL processing
│   │   ├── theme_classifier.py         # Theme classification
│   │   ├── pil_provisions_handler.py   # PIL provisions
│   │   ├── analysis_workflow.py        # Analysis workflow
│   │   └── main_workflow.py            # Main orchestration
│   ├── tools/                          # Analysis tools
│   │   ├── case_analyzer.py            # Core analyzer
│   │   ├── col_extractor.py            # COL extraction
│   │   ├── jurisdiction_detector.py    # Jurisdiction detection
│   │   └── themes_classifier.py        # Theme classification
│   ├── utils/                          # Utility functions
│   │   ├── state_manager.py            # State management
│   │   ├── data_loaders.py             # Data loading
│   │   ├── pdf_handler.py              # PDF processing
│   │   └── themes_extractor.py         # Theme extraction
│   ├── prompts/                        # Prompt templates
│   │   ├── civil_law/                  # Civil law prompts
│   │   ├── common_law/                 # Common law prompts
│   │   └── india/                      # India prompts
│   ├── data/                           # Application data
│   │   ├── themes.csv                  # PIL theme taxonomy
│   │   └── jurisdictions.csv           # Jurisdiction data
│   └── tests/                          # Test suite
├── latam_case_analysis/                # LATAM module
│   ├── pdf_extractor.py                # PDF extraction from Airtable
│   └── txt_converter.py                # Text conversion
└── docs/                               # Documentation
```

### Key Files to Check When Making Changes
- **Config files**: `src/config.py`, `.env.example`
- **Environment**: `.env` (created from .env.example)
- **Main entry point**: `src/app.py`
- **Dependencies**: `pyproject.toml`, `uv.lock`

### Data Formats
- **Themes**: CSV format (`src/data/themes.csv`) for PIL theme taxonomy
- **Jurisdictions**: CSV format (`src/data/jurisdictions.csv`) for jurisdiction reference data
- **Demo case**: BGE 132 III 285 Swiss court case (loaded via `utils/sample_cd.py`)

### API Integration
- **OpenAI**: Primary and only LLM provider (GPT models via langchain-openai)
- **Airtable**: Optional data source for LATAM module only (requires AIRTABLE_API_KEY, AIRTABLE_BASE_ID)
- **PostgreSQL**: Optional database for saving analysis results

### Performance Notes
- **Streamlit startup**: App takes ~5-10 seconds to fully load
- **Install time**: Dependencies take ~60 seconds with pip, faster with uv
- **LLM processing**: Each analysis step takes 10-30 seconds depending on model and case complexity
- **Memory usage**: LLM processing can be memory intensive for longer court decisions

## Troubleshooting

### Common Issues
1. **ModuleNotFoundError for 'pymupdf4llm'**: Install with `pip install pymupdf4llm`
2. **ModuleNotFoundError for 'psycopg2'**: Install with `pip install psycopg2-binary`
3. **OPENAI_API_KEY not set**: Copy .env.example to .env and set your API key
4. **Streamlit won't start**: Check you're in `src/` directory or run from root with `streamlit run src/app.py`
5. **Test import errors**: Tests need to be run from `src/` directory: `cd src && pytest tests/`
6. **Import errors from src/**: Python path issues - run from correct directory

### Expected Timeouts
- **pip/uv install**: 180+ seconds (NEVER CANCEL)
- **Streamlit app startup**: 30+ seconds (NEVER CANCEL)
- **LLM API calls**: 30-60 seconds per call (NEVER CANCEL)
- **Test execution**: 300+ seconds (NEVER CANCEL)

### Environment Variables Required
```bash
# Required for LLM functionality
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-nano  # Or your preferred model

# Optional for database persistence
SQL_CONN_STRING=postgresql+psycopg2://user:pass@host:port/db

# Optional for authentication
USER_CREDENTIALS='{"username":"password"}'

# Optional for LATAM module (Airtable integration)
AIRTABLE_API_KEY=your_airtable_key
AIRTABLE_BASE_ID=your_base_id
```