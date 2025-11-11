# CoLD Case Analyzer - Choice of Law Dataverse

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Environment Setup

- **Python Version**: Python 3.12.3 (specified in `.python-version`)
- **Package Manager**: Uses `uv` for dependency management (modern Python package manager) or `pip`
- **NEVER CANCEL** build or install commands - they may take several minutes
- Bootstrap the repository:

  ```bash
  # Create environment file from template
  cp .env.example .env

  # Edit .env and add your OPENAI_API_KEY

  # Install dependencies using uv (recommended if available)
  uv sync

  # OR install using pip (if uv not available)
  pip install -e .
  ```

### Running the Application

#### Streamlit Web Application (Primary Interface)

- **Entry point**: `streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0`
- **Working directory**: Run from repository root
- **URL**: http://localhost:8501
- **Demo data**: Click "Use Demo Case" button in the UI to load a Swiss court case for testing
- **Features**:
  - Interactive case analysis workflow with step-by-step validation
  - Jurisdiction detection (Civil Law, Common Law, India)
  - Choice of Law section extraction with user feedback
  - Legal theme classification against predefined taxonomy
  - Comprehensive analysis phases: Abstract, Relevant Facts, PIL Provisions, Choice of Law Issue, Court's Position
  - PDF upload support for court decisions
  - Optional user authentication and database persistence
- **Authentication**: Optional login system (credentials in `USER_CREDENTIALS` env var)
- **Dependencies**: Requires `OPENAI_API_KEY` in .env file; optional PostgreSQL database connection

### Docker Setup

- **Location**: `Dockerfile` in repository root
- Docker support available but native Python environment recommended for development
- Docker configuration generates necessary Streamlit secrets from environment variables

### Testing

- **Test location**: `src/tests/`
- **Run tests**:

  ```bash
  # Run all tests
  pytest src/tests/ -v

  # Run specific test file
  pytest src/tests/test_prompt_logic.py -v
  ```

- **Requirements**:
  - Set `OPENAI_API_KEY=test_key` in .env file for tests that don't require actual API calls
  - Some tests may require actual OpenAI API access
  - Tests cover prompt logic, workflow integration, system prompts, and full analysis workflow
- **Test timeout**: Set timeout to 300+ seconds for integration test runs. NEVER CANCEL.

### Linting and Code Quality

- **Linter**: Uses `ruff` for linting and code formatting (install with dev dependencies)
- **Type Checker**: Uses `pyright` for static type checking (install with dev dependencies)
- **Installing dev tools**:
  ```bash
  # Install dev dependencies
  pip install pytest pytest-asyncio pytest-mock ruff pyright
  ```
- **Run linting**:
  ```bash
  ruff check src/
  ruff format src/
  ```
- **Configuration**: See `pyproject.toml` for linting rules

## Coding Conventions

### Logging

- Use `logging` instead of `print` statements in application code
- Import at module level: `import logging` and `logger = logging.getLogger(__name__)`
- Use appropriate log levels:
  - `logger.debug()` for detailed diagnostic information (prompts, responses, intermediate values)
  - `logger.info()` for general informational messages
  - `logger.warning()` for potentially problematic situations
  - `logger.error()` for serious problems
- DO NOT use section header logs like `logger.debug("--- SECTION NAME ---")` - the logger already includes module context via `__name__`
- Print statements are acceptable in: scripts (`populate_readme.py`), test files, and `if __name__ == "__main__"` blocks

### Comments

- Minimize comments - let the code explain what it does
- Only comment to explain **why** something is done, not **what** is being done
- Remove comments that simply repeat function names or obvious operations
- Keep comments that explain design choices, edge cases, or non-obvious requirements

## Validation

### Always perform these validation steps after making changes:

1. **Basic Python environment**:

   ```bash
   python --version  # Should show Python 3.12.3

   # Install dependencies (use uv if available, otherwise pip)
   uv sync
   # OR
   pip install -e .

   python -c "import streamlit; print('✓ Streamlit works')"
   ```

2. **Streamlit Application Validation**:

   ```bash
   cd /home/runner/work/cold-case-analysis/cold-case-analysis
   streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
   # Navigate to http://localhost:8501
   # Click "Use Demo Case" button
   # Verify case data loads and "Detect Jurisdiction" button appears
   ```

3. **Run tests**:

   ```bash
   pytest src/tests/ -v --tb=short
   ```

4. **Lint check**:
   ```bash
   ruff check src/
   ```

## Common Tasks

### Repository Structure

```
cold-case-analysis/
├── .github/
│   └── copilot-instructions.md        # This file - Copilot agent instructions
├── src/                                # Main application source code
│   ├── app.py                          # Streamlit application entry point
│   ├── config.py                       # Application configuration
│   ├── components/                     # UI components and workflow phases
│   │   ├── auth.py                     # Authentication & model selection
│   │   ├── input_handler.py            # Case input handling (PDF, text, demo)
│   │   ├── jurisdiction.py             # Jurisdiction detection phase
│   │   ├── col_processor.py            # Choice of Law extraction phase
│   │   ├── themes.py                   # Theme classification phase
│   │   ├── confidence_display.py       # Confidence display component
│   │   ├── analysis_workflow.py        # Analysis workflow execution
│   │   ├── pil_provisions_handler.py   # PIL provisions extraction
│   │   ├── main_workflow.py            # Main workflow orchestration
│   │   ├── sidebar.py                  # Sidebar rendering
│   │   ├── database.py                 # Database persistence
│   │   └── css.py                      # Custom CSS styling
│   ├── models/                         # Data models (Pydantic)
│   │   ├── analysis_models.py          # Analysis output models
│   │   └── classification_models.py    # Classification models
│   ├── tools/                          # Analysis tools and LLM integration
│   │   ├── jurisdiction_detector.py    # Legal system type detection
│   │   ├── jurisdiction_classifier.py  # Precise jurisdiction classification
│   │   ├── col_extractor.py            # Choice of Law section extraction
│   │   ├── theme_classifier.py         # Theme classification
│   │   ├── case_analyzer.py            # Main case analysis logic
│   │   ├── abstract_generator.py       # Abstract generation
│   │   ├── relevant_facts_extractor.py # Facts extraction
│   │   ├── pil_provisions_extractor.py # PIL provisions extraction
│   │   ├── col_issue_extractor.py      # COL issue extraction
│   │   ├── courts_position_extractor.py  # Court position extraction
│   │   ├── obiter_dicta_extractor.py   # Obiter dicta (Common Law)
│   │   ├── dissenting_opinions_extractor.py  # Dissenting opinions (Common Law)
│   │   └── case_citation_extractor.py  # Case citation extraction
│   ├── utils/                          # Utility functions
│   │   ├── state_manager.py            # Session state management
│   │   ├── data_loaders.py             # Data loading utilities
│   │   ├── pdf_handler.py              # PDF processing
│   │   ├── system_prompt_generator.py  # Dynamic system prompt generation
│   │   ├── themes_extractor.py         # Theme extraction utilities
│   │   ├── debug_print_state.py        # Debug utilities
│   │   └── sample_cd.py                # Sample court decision data
│   ├── prompts/                        # Prompt templates by jurisdiction
│   │   ├── legal_system_type_detection.py    # Legal system detection prompt
│   │   ├── precise_jurisdiction_detection_prompt.py  # Jurisdiction detection
│   │   ├── prompt_selector.py          # Dynamic prompt selection logic
│   │   ├── civil_law/                  # Civil law jurisdiction prompts
│   │   ├── common_law/                 # Common law jurisdiction prompts
│   │   ├── india/                      # India-specific prompts
│   │   └── README.md                   # Prompt documentation (auto-generated)
│   ├── data/                           # Data files
│   │   ├── jurisdictions.csv           # Jurisdiction reference data
│   │   └── themes.csv                  # Legal theme taxonomy
│   └── tests/                          # Test suite
│       ├── test_prompt_logic.py        # Prompt selection logic tests
│       ├── test_dynamic_prompts.py     # Dynamic prompt generation tests
│       ├── test_system_prompts.py      # System prompt tests
│       ├── test_workflow_integration.py # Workflow integration tests
│       └── test_full_workflow.py       # End-to-end workflow tests
├── docs/                               # Documentation
│   ├── QUICK_START.md                  # Quick start guide
│   ├── ARCHITECTURE.md                 # Architecture documentation
│   ├── WORKFLOWS.md                    # Workflow documentation
│   └── DYNAMIC_SYSTEM_PROMPTS_README.md  # Dynamic prompts documentation
├── pyproject.toml                      # Project configuration & dependencies
├── uv.lock                             # Dependency lock file
├── .env.example                        # Environment variables template
├── Dockerfile                          # Docker configuration
└── README.md                           # Main project documentation
```

### Key Files to Check When Making Changes

- **Config files**: `src/config.py`
- **Environment**: `.env` (created from `.env.example`)
- **Main entry point**: `src/app.py`
- **Dependencies**: `pyproject.toml` (modern Python project configuration)
- **Prompt templates**: Files in `src/prompts/civil_law/`, `src/prompts/common_law/`, `src/prompts/india/`
- **Workflow components**: Files in `src/components/`
- **Analysis tools**: Files in `src/tools/`

### Data Files

- **Jurisdiction reference**: `src/data/jurisdictions.csv` - Maps jurisdictions to legal systems
- **Theme taxonomy**: `src/data/themes.csv` - Legal themes for classification
- **Demo case**: Embedded in code via `src/utils/data_loaders.py`

### API Integration

- **OpenAI**: Primary LLM provider (GPT-4o, GPT-4o-mini models, configurable in `src/config.py`)
- **Model selection**: Available through UI, different models for authenticated vs guest users
- **Airtable**: Optional external data source (configured via environment variables)
- **NocoDB**: Optional NoCode database interface
- **PostgreSQL**: Optional database for persistence (configured via `SQL_CONN_STRING`)

### Dynamic System Prompts

The application uses **jurisdiction-specific system prompts** that are dynamically generated based on:

- Detected legal system type (Civil Law, Common Law, India)
- Precise jurisdiction (e.g., Switzerland, USA, India)
- Analysis phase (jurisdiction detection, CoL extraction, theme classification, analysis)

See `src/utils/system_prompt_generator.py` and `docs/DYNAMIC_SYSTEM_PROMPTS_README.md` for details.

### Performance Notes

- **Streamlit startup**: App takes ~5-10 seconds to fully load
- **Install time**: Dependencies installation takes ~60 seconds with uv
- **LLM analysis**: Each analysis step can take 10-30 seconds depending on case complexity
- **Memory usage**: LLM processing can be memory intensive for longer court decisions

## Troubleshooting

### Common Issues

1. **OPENAI_API_KEY not set**:

   - Copy `.env.example` to `.env` and add your API key
   - Required format: `OPENAI_API_KEY="sk-your-key-here"`

2. **ModuleNotFoundError**:

   - Run `uv sync` or `pip install -e .` to install all dependencies
   - Ensure you're using Python 3.12.3

3. **Streamlit won't start**:

   - Check you're running from repository root
   - Command: `streamlit run src/app.py`
   - Verify OPENAI_API_KEY is set in .env

4. **Test failures**:

   - Ensure OPENAI_API_KEY is set (can use dummy value like "test_key" for some tests)
   - Run from repository root: `pytest src/tests/ -v`

5. **Import errors in tests**:

   - Tests may have hardcoded paths that need adjustment
   - Check sys.path modifications in test files

6. **Linting errors**:
   - Run `ruff check src/` to see issues
   - Run `ruff format src/` to auto-fix formatting
   - Configuration in `pyproject.toml`

### Expected Timeouts

- **uv sync or pip install -e .**: 120+ seconds (NEVER CANCEL)
- **Streamlit app startup**: 30+ seconds (NEVER CANCEL)
- **LLM API calls**: 30-60 seconds per call (NEVER CANCEL)
- **Test execution**: 300+ seconds for full suite (NEVER CANCEL)

### Environment Variables Required

See `.env.example` for complete configuration. Key variables:

```bash
# REQUIRED - LLM functionality
OPENAI_API_KEY="sk-your-openai-api-key-here"
OPENAI_MODEL="gpt-5-nano"  # Default model

# OPTIONAL - Database persistence
SQL_CONN_STRING="postgresql+psycopg2://username:password@host:port/database"

# OPTIONAL - External data sources
AIRTABLE_API_KEY="your_airtable_api_key"
AIRTABLE_BASE_ID="your_airtable_base_id"
NOCODB_BASE_URL="https://your-nocodb-instance/api/v1/db/data/noco/project_id"
NOCODB_API_TOKEN="your_nocodb_api_token"

# OPTIONAL - Authentication (JSON format)
USER_CREDENTIALS='{"admin":"password","user":"password"}'

# OPTIONAL - PostgreSQL (for Docker deployment)
POSTGRESQL_HOST="localhost"
POSTGRESQL_PORT="5432"
POSTGRESQL_DATABASE="database_name"
POSTGRESQL_USERNAME="username"
POSTGRESQL_PASSWORD="password"
```

## Development Workflow

### Making Changes

1. **Create a new feature/fix**: Work on focused, minimal changes
2. **Test locally**: Run the Streamlit app and verify changes work
3. **Run tests**: `pytest src/tests/ -v` to ensure nothing breaks
4. **Lint code**: `ruff check src/` and fix any issues
5. **Update documentation**: If you change prompts, run `python src/prompts/populate_readme.py`

### Adding New Prompts

1. Add prompt file in appropriate jurisdiction folder (`src/prompts/civil_law/`, `common_law/`, or `india/`)
2. Follow naming convention: `*_prompt.py` with uppercase `*_PROMPT` variables
3. Run `python src/prompts/populate_readme.py` to update `src/prompts/README.md`
4. Test prompt selection logic: `pytest src/tests/test_prompt_logic.py -v`

### Modifying Workflows

1. Workflow phases are in `src/components/`
2. Main orchestration in `src/components/main_workflow.py`
3. Each phase component handles its own UI, state management, and LLM calls
4. Test changes with the Streamlit app using the "Use Demo Case" button
