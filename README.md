# CoLD Case Analyzer

The CoLD Case Analyzer is a Streamlit-based web application that processes court decisions for private international law (PIL) content extraction and analysis. The system implements an eight-phase workflow where users input judicial decisions through PDF upload, text entry, or pre-loaded demo cases, and the application applies AI models (primarily OpenAI GPT) to extract and categorize PIL-relevant information.

## Key Features

- **Interactive Analysis Workflow**: Step-by-step processing with user validation at each stage
- **Jurisdiction Detection**: Automatically identifies legal system (Civil Law, Common Law, or Indian law)
- **Choice of Law Extraction**: Identifies and extracts relevant PIL sections from court decisions
- **Theme Classification**: Categorizes cases against a predefined PIL taxonomy
- **Comprehensive Legal Analysis**: Extracts abstracts, facts, provisions, legal issues, and court reasoning
- **User Feedback Integration**: Allows manual validation and editing at each analysis phase
- **Database Persistence**: Stores analyses with user identification and timestamps
- **Demo Case Support**: Includes BGE 132 III 285 Swiss court case for testing
- **LLM Monitoring**: Integrated Logfire instrumentation for tracking AI model performance and costs

## System Architecture

The application processes cases through sequential steps:

1. **Input Phase**: PDF upload, text entry, or demo case selection
2. **Jurisdiction Detection**: Identifies the legal system and jurisdiction
3. **COL Section Extraction**: Extracts Choice of Law sections with user validation
4. **Theme Classification**: Categorizes against PIL themes with scoring
5. **Detailed Analysis**: Five-component analysis (abstract, facts, provisions, issue, position)
6. **Database Storage**: Saves completed analyses for future reference

The codebase uses modular components for authentication, input processing, database operations, and analysis phases. Jurisdiction-specific prompt engineering is implemented through separate template sets for different legal systems (civil law, common law, India).

## Project Structure

```
cold-case-analysis/
├── src/                          # Main application source code
│   ├── app.py                    # Streamlit app entry point
│   ├── config.py                 # Configuration and initialization
│   ├── components/               # UI components
│   │   ├── auth.py              # Authentication & model selection
│   │   ├── database.py          # Database persistence
│   │   ├── input_handler.py    # Case input handling
│   │   ├── jurisdiction.py     # Jurisdiction detection
│   │   ├── col_processor.py    # Choice of Law processing
│   │   ├── themes.py           # Theme classification
│   │   ├── confidence_display.py  # Confidence scores display
│   │   ├── pil_provisions_handler.py  # PIL provisions extraction
│   │   ├── analysis_workflow.py # Main analysis workflow
│   │   ├── main_workflow.py    # Workflow orchestration
│   │   ├── sidebar.py          # Sidebar component
│   │   └── css.py              # Custom styling
│   ├── models/                   # Data models (Pydantic)
│   │   ├── analysis_models.py  # Analysis output models
│   │   └── classification_models.py  # Classification models
│   ├── utils/                    # Utility functions
│   │   ├── state_manager.py    # Session state management
│   │   ├── data_loaders.py     # Data loading utilities
│   │   ├── pdf_handler.py      # PDF text extraction
│   │   ├── themes_extractor.py # Theme extraction logic
│   │   ├── system_prompt_generator.py  # Dynamic prompt generation
│   │   ├── debug_print_state.py  # Debug utilities
│   │   └── sample_cd.py        # Sample court decision data
│   ├── tools/                    # Analysis tools
│   │   ├── case_analyzer.py    # Core case analysis
│   │   ├── col_extractor.py    # COL section extraction
│   │   ├── jurisdiction_detector.py    # Jurisdiction detection
│   │   ├── jurisdiction_classifier.py  # Precise jurisdiction classification
│   │   ├── theme_classifier.py # Theme classification
│   │   ├── abstract_generator.py  # Abstract generation
│   │   ├── relevant_facts_extractor.py  # Facts extraction
│   │   ├── pil_provisions_extractor.py  # PIL provisions extraction
│   │   ├── col_issue_extractor.py  # COL issue extraction
│   │   ├── courts_position_extractor.py  # Court position extraction
│   │   ├── obiter_dicta_extractor.py  # Obiter dicta extraction (Common Law)
│   │   ├── dissenting_opinions_extractor.py  # Dissenting opinions (Common Law)
│   │   └── case_citation_extractor.py  # Case citation extraction
│   ├── prompts/                  # Prompt templates
│   │   ├── civil_law/          # Civil law jurisdiction prompts
│   │   ├── common_law/         # Common law jurisdiction prompts
│   │   └── india/              # Indian law jurisdiction prompts
│   ├── data/                     # Application data
│   │   ├── themes.csv          # PIL theme taxonomy
│   │   └── jurisdictions.csv   # Jurisdiction data
│   └── tests/                    # Test suite
├── docs/                         # Documentation
├── Dockerfile                    # Docker deployment
├── pyproject.toml               # Python project configuration
├── uv.lock                      # Dependency lock file
└── .env.example                 # Environment configuration template
```

## Component Architecture

`src/app.py` is the main entry point that handles: page config, authentication initialization, model selection, CSS/sidebar loading, and main workflow rendering.

The core workflow logic is distributed across the following components:

### Components (`components/`)

#### `auth.py`

- Authentication and model selection functionality
- Functions: `initialize_auth()`, `render_model_selector()`

#### `database.py`

- Database persistence functionality
- Functions: `save_to_db()`

#### `input_handler.py`

- Input handling for case citation, email, PDF upload, text input, demo case
- Functions: `render_pdf_uploader()`, `render_text_input()`, `render_input_phase()`

#### `jurisdiction.py`

- Enhanced jurisdiction detection with precise jurisdiction identification
- Functions: `render_jurisdiction_detection()`, `get_final_jurisdiction_data()`

#### `col_processor.py`

- Choice of Law section processing and feedback
- Functions: `display_jurisdiction_info()`, `display_col_extractions()`, `handle_col_feedback_phase()`

#### `themes.py`

- Theme classification and editing interface
- Functions: `display_theme_classification()`, `handle_theme_editing()`, `render_theme_classification()`

#### `confidence_display.py`

- Confidence score display with reasoning
- Functions: `render_confidence_chip()`, `render_confidence_modal()`, `add_confidence_chip_css()`

#### `pil_provisions_handler.py`

- PIL provisions extraction and processing
- Functions: `display_pil_provisions()`, `handle_pil_provisions_editing()`, `parse_pil_provisions()`, `format_pil_for_display()`, `format_pil_for_storage()`, `update_pil_provisions_state()`

#### `analysis_workflow.py`

- Analysis workflow execution and management
- Functions: `render_email_input()`, `display_completion_message()`, `render_results_as_markdown()`

#### `main_workflow.py`

- Main workflow orchestration
- Functions: `render_initial_input_phase()`, `render_processing_phases()`, `render_main_workflow()`

#### `sidebar.py`

- Sidebar navigation and information display
- Functions: `render_sidebar()`

#### `css.py`

- Custom CSS styling for the application
- Functions: `load_css()`

Utilities are further specified under:

### Configuration (`config.py`)

The main configuration module that initializes the application environment:

- **Environment Setup**: Loads environment variables from `.env` file
- **Logging Configuration**: Sets up application-wide logging
- **LLM Clients**: Provides factory functions for OpenAI clients
  - `get_llm()`: Returns a LangChain ChatOpenAI instance
  - `get_openai_client()`: Returns an OpenAI client instance
- **Logfire Monitoring**: Configures and instruments:
  - OpenAI API calls for automatic tracing
  - HTTP requests via requests library
  - PostgreSQL database calls via psycopg2
- **Model Selection**: Supports configurable model selection via environment variables

Key environment variables required:

- `OPENAI_API_KEY` (required): OpenAI API key for LLM functionality
- `OPENAI_MODEL` (optional): Default model to use (defaults to "gpt-5-nano")
- `LOGFIRE_TOKEN` (optional): Token for Logfire monitoring service

### Data Models (`models/`)

Pydantic models that define structured outputs for analysis and classification tasks. These models ensure type safety and validation throughout the application.

#### `analysis_models.py`

Output models for case analysis steps:

- **`ColSectionOutput`**: Choice of Law section extraction results
  - `col_sections: list[str]` - List of extracted COL section texts
  - `confidence: Literal["low", "medium", "high"]` - Confidence level
  - `reasoning: str` - Explanation of extraction
- **`CaseCitationOutput`**: Case citation extraction results
  - `case_citation: str` - Extracted academic-format citation
  - `confidence` and `reasoning` fields
- **`RelevantFactsOutput`**: Relevant facts extraction results
  - `relevant_facts: str` - Factual background of the case
  - `confidence` and `reasoning` fields
- **`PILProvisionsOutput`**: PIL provisions extraction results
  - `pil_provisions: list[str]` - List of legal provisions cited
  - `confidence` and `reasoning` fields
- **`ColIssueOutput`**: Choice of Law issue identification results
  - `col_issue: str` - The COL issue(s) in the case
  - `confidence` and `reasoning` fields
- **`CourtsPositionOutput`**: Court's position analysis results
  - `courts_position: str` - Court's reasoning and decision
  - `confidence` and `reasoning` fields
- **`ObiterDictaOutput`**: Obiter dicta extraction results (Common Law)
  - `obiter_dicta: str` - Non-binding statements from opinion
  - `confidence` and `reasoning` fields
- **`DissentingOpinionsOutput`**: Dissenting opinions extraction results (Common Law)
  - `dissenting_opinions: str` - Dissenting judge opinions
  - `confidence` and `reasoning` fields
- **`AbstractOutput`**: Case abstract generation results
  - `abstract: str` - Concise case summary
  - `confidence` and `reasoning` fields

#### `classification_models.py`

Output models for classification tasks:

- **`JurisdictionOutput`**: Jurisdiction detection results
  - `legal_system_type: str` - Type of legal system (e.g., "Civil-law jurisdiction")
  - `precise_jurisdiction: str` - Specific jurisdiction (e.g., "Switzerland")
  - `jurisdiction_code: str` - ISO country code (e.g., "CH")
  - `confidence` and `reasoning` fields
- **`ThemeClassificationOutput`**: PIL theme classification results
  - `themes: list[ThemeWithNA]` - List of classified themes
  - `confidence` and `reasoning` fields
- **`Theme`**: Literal type defining valid PIL themes:
  - "Party autonomy", "Tacit choice", "Partial choice", "Absence of choice"
  - "Arbitration", "Freedom of Choice", "Rules of Law", "Dépeçage"
  - "Public policy", "Mandatory rules", "Consumer contracts", "Employment contracts"
- **`ThemeWithNA`**: Theme type extended with "NA" for non-applicable cases

All models include:

- Type-safe field definitions with Pydantic
- Confidence levels (low, medium, high) for quality assessment
- Reasoning fields for explainability and transparency
- Field descriptions for documentation

Utilities are further specified under:

### Utilities (`utils/`)

#### `state_manager.py`

- Session state management utilities
- Functions: `initialize_col_state()`, `create_initial_analysis_state()`, `update_col_state()`, `get_col_state()`, `load_demo_case()`

#### `data_loaders.py`

- Data loading utilities (themes, demo case)
- Functions: `load_valid_themes()`, `get_demo_case_text()`

#### `pdf_handler.py`

- PDF text extraction utilities
- Functions: `extract_text_from_pdf()`

#### `themes_extractor.py`

- Theme extraction and classification logic
- Functions: Theme extraction and processing utilities

#### `system_prompt_generator.py`

- Dynamic system prompt generation for different jurisdictions
- Functions: Jurisdiction-specific prompt generation

#### `debug_print_state.py`

- Debug utilities for printing session state
- Functions: Debugging helper functions

#### `sample_cd.py`

- Sample court decision data for testing
- Contains: Demo case text and metadata

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API Key

### Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Choice-of-Law-Dataverse/cold-case-analysis.git
   cd cold-case-analysis
   ```

2. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Install dependencies**:

   Using pip:

   ```bash
   pip install streamlit langchain-core langchain-openai pandas pymupdf4llm psycopg2-binary python-dotenv requests
   ```

   Or using uv (recommended):

   ```bash
   uv sync
   ```

4. **Run the application**:

   ```bash
   # With pip installation
   cd src
   streamlit run app.py

   # With uv
   uv run streamlit run src/app.py
   ```

5. **Open your browser**: Navigate to `http://localhost:8501`

### Using Docker

```bash
# Build the image
docker build -t cold-case-analyzer .

# Run the container
docker run -p 8501:8501 --env-file .env cold-case-analyzer
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

### Required

- `OPENAI_API_KEY`: Your OpenAI API key for LLM functionality
- `OPENAI_MODEL`: Model to use (default: "gpt-5-nano")

### Optional

- `SQL_CONN_STRING`: PostgreSQL connection for storing analysis results
- `USER_CREDENTIALS`: JSON object for user authentication (e.g., `{"admin":"password"}`)
- `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`: For Airtable integration
- `NOCODB_BASE_URL`, `NOCODB_API_TOKEN`: For NoCode database interface

## Usage Examples

### Using the Demo Case

1. Open the application
2. Click "Use Demo Case" button
3. The BGE 132 III 285 case will be automatically loaded
4. Follow the workflow through jurisdiction detection, COL extraction, and theme classification

### Uploading Your Own Case

1. Enter case citation (e.g., "Federal Court, 20.12.2005 - BGE 132 III 285")
2. Either:
   - Upload a PDF file, or
   - Paste the court decision text directly
3. Click "Detect Jurisdiction" to begin analysis
4. Review and validate each analysis step
5. Provide feedback to refine the analysis

### Analyzing Cases

The analysis workflow consists of:

1. **Jurisdiction Detection**: Identify the legal system
2. **COL Extraction**: Extract Choice of Law sections
3. **Theme Classification**: Categorize PIL themes
4. **PIL Provisions**: Extract applicable provisions
5. **Detailed Analysis**: Generate comprehensive legal analysis

At each step, you can:

- Score the AI output (0-100)
- Edit the results
- Provide feedback for refinement

## Development

### Project Structure Conventions

- **Components** (`src/components/`): UI rendering and user interaction
- **Tools** (`src/tools/`): Core analysis logic and LLM interactions
- **Utils** (`src/utils/`): Helper functions and utilities
- **Prompts** (`src/prompts/`): Jurisdiction-specific prompt templates

### Adding a New Analysis Phase

1. Create a new component in `src/components/new_phase.py`:

   ```python
   def render_new_phase(state):
       # Your phase logic here
       pass
   ```

2. Add to `src/components/main_workflow.py`:

   ```python
   from components.new_phase import render_new_phase

   def render_processing_phases():
       # ... existing phases
       render_new_phase(col_state)
   ```

### Adding Jurisdiction-Specific Prompts

1. Create prompts in the appropriate jurisdiction directory:

   - `src/prompts/civil_law/` for civil law jurisdictions
   - `src/prompts/common_law/` for common law jurisdictions
   - `src/prompts/india/` for Indian law

2. Use the prompt selector in `src/prompts/prompt_selector.py` to load jurisdiction-specific prompts

### Testing

Run tests with pytest:

```bash
cd src
pytest tests/ -v
```

## Documentation

- **[Architecture Documentation](docs/ARCHITECTURE.md)**: System architecture and data flow
- **[Quick Start Guide](docs/QUICK_START.md)**: Quick setup instructions
- **[Workflows](docs/WORKFLOWS.md)**: Detailed workflow diagrams
- **[Logfire Monitoring](docs/LOGFIRE_MONITORING.md)**: LLM monitoring and observability setup
- **[Prompts README](src/prompts/README.md)**: Comprehensive prompt documentation

## Contributing

Contributions are welcome! Please ensure:

1. Code follows the coding conventions in `AGENTS.md`
2. Use logging instead of print statements in application code
3. Minimize comments - only explain "why", not "what"
4. Components are properly modularized
5. Tests are added for new functionality
6. Documentation is updated accordingly

## License

This project is part of the Choice of Law Dataverse (CoLD) initiative. For more information, visit [cold.global](https://cold.global/).

## Support

- Check the comprehensive documentation in the `docs/` folder
- Review existing issues in the GitHub repository
- Consult the [CoLD project website](https://cold.global/) for research context
