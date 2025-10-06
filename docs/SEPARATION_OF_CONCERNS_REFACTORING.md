# Separation of Concerns Refactoring

## Overview

This refactoring enforces SOLID principles and separation of concerns across the CoLD Case Analyzer codebase. The main goal is to separate data fetching logic (analysis/AI functions) from state management (UI components).

## Problem Statement

The original codebase had several issues:

1. **State manipulation scattered**: Functions in `tools/` were directly mutating the state dictionary
2. **Poor testability**: Data fetching methods received `state` as parameter, making unit testing difficult
3. **No caching**: Functions with state parameters cannot be cached effectively
4. **Mental model complexity**: Developers had to track state mutations across multiple functions

### Example of Old Code (Anti-pattern)

```python
def relevant_facts(state):
    """Bad: receives state, mutates it directly"""
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    # ... perform analysis ...
    
    # BAD: Directly mutating state
    state.setdefault("relevant_facts", []).append(facts)
    state.setdefault("relevant_facts_confidence", []).append(confidence)
    return result
```

## Solution

### New Architecture

The refactored code follows these principles:

1. **Data fetching methods** (in `tools/`) are pure functions:
   - Accept explicit parameters only
   - Return results without side effects
   - No state mutation
   - No Streamlit imports

2. **Rendering components** (in `components/`) manage state:
   - Extract data from state
   - Call data fetching methods with explicit parameters
   - Update state with returned results
   - Handle all UI rendering

### Example of New Code (Best Practice)

```python
# In tools/case_analyzer.py
def relevant_facts(
    text: str,
    col_section: str,
    jurisdiction: str,
    specific_jurisdiction: str | None,
    model: str,
):
    """
    Good: accepts explicit parameters, returns result without mutation
    
    Args:
        text: Full court decision text
        col_section: Choice of Law section text
        jurisdiction: Legal system type
        specific_jurisdiction: Precise jurisdiction
        model: Model to use for extraction
    
    Returns:
        RelevantFactsOutput: Extracted facts with confidence and reasoning
    """
    # ... perform analysis ...
    return result  # Pure function - no side effects


# In components/analysis_workflow.py
def execute_analysis_step(state, name, func):
    """Component manages state updates"""
    # Extract parameters from state
    text = state["full_text"]
    col_section = state.get("col_section", [""])[-1]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    model = state.get("model") or "gpt-5-nano"
    
    # Call pure function with explicit parameters
    result = func(text, col_section, jurisdiction, specific_jurisdiction, model)
    
    # Update state with results (state management in component)
    state.setdefault("relevant_facts", []).append(result.relevant_facts)
    state.setdefault("relevant_facts_confidence", []).append(result.confidence)
    state.setdefault("relevant_facts_reasoning", []).append(result.reasoning)
```

## Changes Summary

### Files Modified

#### Tools Layer (Data Fetching)
- `src/tools/case_analyzer.py` - All 7 analysis functions refactored:
  - `relevant_facts()` - Now accepts explicit parameters
  - `pil_provisions()` - Now accepts explicit parameters
  - `col_issue()` - Now accepts explicit parameters
  - `courts_position()` - Now accepts explicit parameters
  - `obiter_dicta()` - Now accepts explicit parameters
  - `dissenting_opinions()` - Now accepts explicit parameters
  - `abstract()` - Now accepts explicit parameters

- `src/tools/col_extractor.py`:
  - `extract_col_section()` - Now accepts explicit parameters

- `src/tools/themes_classifier.py`:
  - `theme_classification_node()` - Now accepts explicit parameters

#### Components Layer (State Management)
- `src/components/main_workflow.py`:
  - `render_initial_input_phase()` - Now extracts state and updates after calling `extract_col_section()`

- `src/components/col_processor.py`:
  - `render_feedback_input()` - Now handles state extraction and updates
  - `render_edit_section()` - Now handles state updates after theme classification

- `src/components/analysis_workflow.py`:
  - `execute_analysis_step()` - Now extracts state, calls functions, and updates state
  - `execute_all_analysis_steps_parallel()` - Now manages state for parallel execution

#### Utilities
- `src/utils/system_prompt_generator.py`:
  - Added `generate_system_prompt()` - New helper that accepts explicit parameters instead of state

### Tests Added
- `src/tests/test_separation_of_concerns.py`:
  - Validates function signatures don't accept `state` parameter
  - Validates tools modules don't import Streamlit
  - Validates components can use refactored tools

## Benefits Achieved

### 1. Better Testability
Functions can now be tested in isolation without complex state setup:

```python
# Before: Required full state setup
state = {
    "full_text": "...",
    "jurisdiction": "...",
    "col_section": [...],
    # ... many more fields
}
result = relevant_facts(state)

# After: Simple function call with explicit parameters
result = relevant_facts(
    text="...",
    col_section="...",
    jurisdiction="Civil-law jurisdiction",
    specific_jurisdiction="Switzerland",
    model="gpt-4o"
)
```

### 2. Function Caching
Pure functions with explicit parameters enable caching:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_relevant_facts(text, col_section, jurisdiction, specific_jurisdiction, model):
    return relevant_facts(text, col_section, jurisdiction, specific_jurisdiction, model)
```

### 3. Clearer Code Organization
- **Tools**: Pure data fetching functions
- **Components**: State management and UI rendering
- **Clear separation**: Easy to understand responsibilities

### 4. Better Mental Model
Developers can now:
- Focus on one layer at a time
- Understand data flow more easily
- Debug issues faster (check component for state issues, check tools for analysis issues)

## Migration Guide

If you need to add new analysis functions, follow this pattern:

### ❌ Don't Do This
```python
def new_analysis(state):
    # Extract from state
    text = state["full_text"]
    # ... do analysis ...
    # Mutate state
    state["new_field"] = result
    return result
```

### ✅ Do This Instead

1. **In `tools/` module** - Create pure function:
```python
def new_analysis(text: str, jurisdiction: str, model: str) -> AnalysisOutput:
    """
    Perform new analysis.
    
    Args:
        text: Full court decision text
        jurisdiction: Legal system type
        model: Model to use
        
    Returns:
        AnalysisOutput: Analysis result with confidence and reasoning
    """
    # ... perform analysis ...
    return AnalysisOutput(result=result, confidence=confidence, reasoning=reasoning)
```

2. **In `components/` module** - Handle state:
```python
def execute_new_analysis(state):
    # Extract parameters from state
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    model = state.get("model") or "gpt-5-nano"
    
    # Call pure function
    result = new_analysis(text, jurisdiction, model)
    
    # Update state with results
    state.setdefault("new_field", []).append(result.result)
    state.setdefault("new_field_confidence", []).append(result.confidence)
    state.setdefault("new_field_reasoning", []).append(result.reasoning)
```

## Testing

Run the separation of concerns test:

```bash
cd /home/runner/work/cold-case-analysis/cold-case-analysis
python src/tests/test_separation_of_concerns.py
```

Expected output:
```
✅ ALL SEPARATION OF CONCERNS TESTS PASSED!
- relevant_facts has explicit parameters (no state)
- pil_provisions has explicit parameters (no state)
- col_issue has explicit parameters (no state)
- courts_position has explicit parameters (no state)
- abstract has explicit parameters (no state)
- extract_col_section has explicit parameters (no state)
- theme_classification_node has explicit parameters (no state)
- All tools modules don't import Streamlit
- All components import successfully
```

## Verification

To verify the refactoring:

1. **Lint check**: `ruff check src/`
2. **Import test**: `python -c "from tools.case_analyzer import *"`
3. **Separation test**: `python src/tests/test_separation_of_concerns.py`
4. **Application test**: `streamlit run src/app.py` and test with demo case

## Future Improvements

With this refactoring in place, we can now:

1. **Add unit tests** for individual analysis functions without state setup
2. **Implement caching** for expensive LLM calls
3. **Add parallel processing** more easily (pure functions are thread-safe)
4. **Create alternative UIs** (CLI, API) that use the same tools
5. **Mock analysis functions** for testing components

## Conclusion

This refactoring makes the codebase more maintainable, testable, and follows SOLID principles. The separation of concerns between data fetching and state management provides a clear mental model for developers and enables future enhancements.
