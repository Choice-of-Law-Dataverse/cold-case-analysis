# CoLD Case Analyzer in Streamlit

The CoLD Case Analyzer is a Streamlit-based web application that processes court decisions for private international law (PIL) content extraction and analysis. The system implements an eight-phase workflow where users input judicial decisions through PDF upload, text entry, or pre-loaded examples, and the application applies AI models to extract and categorize PIL-relevant information. The tool requires initial jurisdiction classification (Civil Law, Common Law, or Indian legal systems) which determines which prompt templates are applied during subsequent processing phases.

The application processes cases through sequential steps: jurisdiction detection, choice of law section identification, theme classification against a predefined taxonomy, and a five-component legal analysis covering abstracts, factual background, applicable provisions, legal issues, and court reasoning. Each phase generates AI output that requires user validation through numerical scoring (0-100) and manual editing before progression to the next step. The system maintains session state throughout the workflow and stores completed analyses in a database with user identification, model information, and timestamped interaction history.

The codebase separates concerns across modular components handling authentication, input processing, database operations, and analysis phases, with jurisdiction-specific prompt engineering implemented through separate template sets for different legal systems. Users can access different AI models based on authentication status, with guest access limited to basic models and authenticated users having access to advanced options. The application outputs structured English-language analysis regardless of input language and integrates with the broader CoLD project database for case storage. The tool serves as a systematic processing interface for legal professionals working with international private law cases, though it requires manual oversight and validation at each analytical step.

## Structure

`App.py` is a minimal orchestration script that handles: page config, authentication initialization, model selection, CSS/sidebar loading, and main workflow rendering.

The core workflow logic is distributed across the following components:

### Components (`components/`)

#### `auth.py`
- Authentication and model selection functionality
- Functions: `initialize_auth()`, `render_model_selector()`

#### `database.py`  
- Database persistence functionality
- Functions: `save_to_db()`

#### `input_handler.py`
- Input handling for case citation, PDF upload, text input, demo case
- Functions: `render_case_citation_input()`, `render_pdf_uploader()`, `render_text_input()`, `render_demo_button()`, `render_input_phase()`

#### `col_processor.py`
- Choice of Law section processing and feedback
- Functions: `display_jurisdiction_info()`, `display_case_info()`, `display_col_extractions()`, `handle_first_extraction_scoring()`, `handle_col_feedback_phase()`, `render_col_processing()`

#### `theme_classifier.py`
- Theme classification and editing interface
- Functions: `display_theme_classification()`, `handle_theme_scoring()`, `handle_theme_editing()`, `display_final_themes()`, `render_theme_classification()`

#### `analysis_workflow.py`
- Analysis workflow execution and management
- Functions: `display_analysis_history()`, `display_completion_message()`, `get_analysis_steps()`, `execute_analysis_step()`, `handle_step_scoring()`, `handle_step_editing()`, `process_current_analysis_step()`, `render_analysis_workflow()`

#### `main_workflow.py`
- Main workflow orchestration
- Functions: `render_initial_input_phase()`, `render_processing_phases()`, `render_main_workflow()`

Utilities are further specified under:

### Utilities (`utils/`)

#### `state_manager.py`
- Session state management utilities
- Functions: `initialize_col_state()`, `create_initial_analysis_state()`, `update_col_state()`, `get_col_state()`, `load_demo_case()`

#### `data_loaders.py`
- Data loading utilities (themes, demo case)
- Functions: `load_valid_themes()`, `get_demo_case_text()`

## Usage Examples

### Adding a New Phase
```python
# Create components/new_phase.py
def render_new_phase(state):
    # Your phase logic here
    pass

# Add to components/main_workflow.py
from components.new_phase import render_new_phase

def render_processing_phases():
    # ... existing phases
    render_new_phase(col_state)
```

### Modifying Input Handling
```python
# All input-related changes go in components/input_handler.py
def render_new_input_type():
    # New input widget logic
    pass
```

### Testing Individual Components
```python
# Test components in isolation
from components.theme_classifier import handle_theme_scoring

def test_theme_scoring():
    mock_state = {"theme_first_score_submitted": False}
    result = handle_theme_scoring(mock_state)
    assert result == False
```