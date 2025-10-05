# Implementation Summary: Agentic Workflow with Structured Outputs

## Overview

This implementation replaces LangChain-based LLM calls with OpenAI's structured outputs using Pydantic models, adds confidence tracking, and implements a UI for displaying confidence levels.

## Key Changes

### 1. Pydantic Models for Structured Outputs

Created comprehensive Pydantic models in `src/models/` for all LLM outputs:

**Classification Models** (`src/models/classification_models.py`):

- `JurisdictionOutput`: Legal system type, precise jurisdiction, country code, confidence, reasoning
- `ThemeClassificationOutput`: List of themes, confidence, reasoning

**Analysis Models** (`src/models/analysis_models.py`):

- `ColSectionOutput`: Choice of Law section text, confidence, reasoning
- `RelevantFactsOutput`: Relevant facts, confidence, reasoning
- `PILProvisionsOutput`: List of PIL provisions, confidence, reasoning
- `ColIssueOutput`: CoL issue text, confidence, reasoning
- `CourtsPositionOutput`: Court's position, confidence, reasoning
- `ObiterDictaOutput`: Obiter dicta, confidence, reasoning
- `DissentingOpinionsOutput`: Dissenting opinions, confidence, reasoning
- `AbstractOutput`: Abstract text, confidence, reasoning

All models follow this pattern:

```python
class OutputModel(BaseModel):
    primary_field: str  # or list[str]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level")
    reasoning: str = Field(description="Explanation of the analysis")
```

### 2. Backend Updates

**Config** (`src/config.py`):

- Added `get_openai_client()` function to create OpenAI client instances
- Kept existing `get_llm()` for backward compatibility

**Analysis Tools** - Replaced LangChain calls with structured outputs:

`src/tools/case_analyzer.py`:

- Added `_call_openai_structured()` helper function
- Updated all 7 analysis functions:
  - `relevant_facts()`
  - `pil_provisions()`
  - `col_issue()`
  - `courts_position()`
  - `obiter_dicta()`
  - `dissenting_opinions()`
  - `abstract()`
- Each function now stores `{name}_confidence` and `{name}_reasoning` in state

`src/tools/col_extractor.py`:

- Updated `extract_col_section()` to use `ColSectionOutput`
- Stores confidence and reasoning

`src/tools/themes_classifier.py`:

- Updated `theme_classification_node()` to use `ThemeClassificationOutput`
- Stores confidence and reasoning

`src/tools/precise_jurisdiction_detector.py`:

- Added new `detect_precise_jurisdiction_with_confidence()` function
- Returns dict with jurisdiction data including confidence/reasoning
- Kept legacy `detect_precise_jurisdiction()` for backward compatibility

### 3. UI Components for Confidence Display

**Confidence Display Component** (`src/components/confidence_display.py` - NEW):

- `render_confidence_chip()`: Displays purple chip button with confidence percentage
- `render_confidence_modal()`: Modal dialog showing confidence and reasoning
- `add_confidence_chip_css()`: Custom CSS for purple chip styling (#9b4dca)

**Updated UI Components**:

`src/components/jurisdiction_detection.py`:

- Displays confidence chip for jurisdiction detection results
- Uses new `detect_precise_jurisdiction_with_confidence()` function
- Stores confidence and reasoning in session state

`src/components/col_processor.py`:

- Shows confidence chip next to "Edit extracted Choice of Law section" title
- Retrieves confidence/reasoning from state

`src/components/theme_classifier.py`:

- Shows confidence chip next to "Theme Classification" title
- Retrieves confidence/reasoning from state

`src/components/analysis_workflow.py`:

- Updated `render_final_editing_phase()` to show confidence chips for all analysis steps
- Each textarea has a confidence chip displayed in a column layout

### 4. State Structure Changes

For each analysis step, the state now includes three lists:

- `{step_name}`: List of outputs (existing)
- `{step_name}_confidence`: List of confidence values (new)
- `{step_name}_reasoning`: List of reasoning explanations (new)

Example:

```python
state = {
    "relevant_facts": ["The case involves..."],
    "relevant_facts_confidence": [0.87],
    "relevant_facts_reasoning": ["High confidence because..."],
    # ... other fields
}
```

## How It Works

### LLM Call Flow

1. Component calls analysis function (e.g., `relevant_facts(state)`)
2. Function builds prompt from templates (unchanged)
3. Function calls `_call_openai_structured(prompt, system_prompt, PydanticModel, model)`
4. Helper function:
   - Gets OpenAI client
   - Calls `client.beta.chat.completions.parse()` with Pydantic model as response_format
   - Returns parsed Pydantic model instance
5. Function extracts fields from Pydantic model:
   - Main output (e.g., `result.relevant_facts`)
   - `result.confidence`
   - `result.reasoning`
6. Function stores all three in state
7. Function returns updated state dict

### UI Display Flow

1. Component renders analysis step
2. Component retrieves confidence and reasoning from state:
   ```python
   confidence = state.get(f"{step_name}_confidence", [0.0])[-1]
   reasoning = state.get(f"{step_name}_reasoning", [""])[-1]
   ```
3. Component displays title and confidence chip in columns:
   ```python
   col1, col2 = st.columns([0.7, 0.3])
   with col1:
       st.markdown("**Step Title**")
   with col2:
       render_confidence_chip(confidence, reasoning, unique_key)
   ```
4. User clicks chip → modal opens showing confidence and reasoning
5. User clicks "Close" → modal closes

## Benefits

1. **Type Safety**: Pydantic validates all LLM outputs
2. **No Manual Parsing**: Structured outputs eliminate JSON parsing errors
3. **Confidence Tracking**: Every step has explicit confidence level
4. **Transparency**: Users can see reasoning behind each analysis
5. **Better UX**: Visual confidence indicators help users trust the system
6. **Maintainability**: Cleaner code with defined schemas

## Testing

All imports validated:

```bash
python -c "from models import *; from tools import *; from components import *"
# ✓ All imports successful
```

Pydantic models validated:

```bash
python -c "from models.classification_models import JurisdictionOutput; print(JurisdictionOutput.model_json_schema())"
# ✓ Schema valid with fields: legal_system_type, precise_jurisdiction, jurisdiction_code, confidence, reasoning
```

## Notes

- The implementation uses OpenAI's structured outputs feature instead of the openai-agents-python library
- This approach is more minimal and achieves the same goals
- Workflow logic unchanged - only internals updated
- Backward compatible with existing state structure
- Ready for testing with actual OpenAI API key
