# CoLD Case Analyzer - Coding Style Guide

This document outlines the coding standards and best practices for contributing to the CoLD Case Analyzer project.

## Logging Guidelines

### Use Logging, Not Print Statements

**❌ Don't do this:**
```python
print(f"Processing case: {case_id}")
print(f"Prompting LLM with:\n{prompt}\n")
```

**✅ Do this:**
```python
logger.debug("Processing case: %s", case_id)
logger.debug("Prompting LLM with: %s", prompt)
```

### Logging Levels

Use appropriate logging levels for different types of messages:

- **`logger.debug()`**: Detailed diagnostic information (prompts, responses, intermediate values)
- **`logger.info()`**: General informational messages about program flow
- **`logger.warning()`**: Warning messages for potentially problematic situations
- **`logger.error()`**: Error messages for serious problems
- **`logger.critical()`**: Critical errors that may cause the program to terminate

### Setting Up Logging

Import logging and create a logger at the module level:

```python
import logging

logger = logging.getLogger(__name__)
```

### When to Use Print Statements

Print statements are acceptable in:
- **Scripts** (e.g., `populate_readme.py`) for user-facing output
- **Test files** for test results and debugging
- **Command-line tools** for direct user interaction

## Comment Guidelines

### Only Comment When Necessary

Comments should explain **why** something is done, not **what** is being done. The code itself should be clear enough to explain what it does.

**❌ Don't do this (redundant comments):**
```python
# Get last col_section (string)
col_section = ""
sections = state.get("col_section", [])
if sections:
    col_section = sections[-1]

# Get dynamic system prompt based on jurisdiction
system_prompt = get_system_prompt_for_analysis(state)

# append relevant facts
state.setdefault("relevant_facts", []).append(facts)
```

**✅ Do this (clear code, minimal comments):**
```python
col_section = ""
sections = state.get("col_section", [])
if sections:
    col_section = sections[-1]

system_prompt = get_system_prompt_for_analysis(state)

state.setdefault("relevant_facts", []).append(facts)
```

### When to Use Comments

Use comments to:
1. **Explain design choices**: Why you chose a particular approach over alternatives
2. **Document complex logic**: When the code is inherently complex and needs explanation
3. **Provide context**: Historical context, edge cases, or non-obvious requirements
4. **Mark sections**: Use section headers for major functional blocks (sparingly)

**✅ Good use of comments:**
```python
# Using jurisdiction mapping first before LLM analysis to save API costs
jurisdiction_based_result = detect_legal_system_by_jurisdiction(jurisdiction_name)
if jurisdiction_based_result:
    return jurisdiction_based_result

# Fallback: Apply inversion test - statement is obiter if decision would 
# remain the same if statement were omitted or reversed
if could_decision_stand_without(statement):
    obiter_statements.append(statement)
```

### Section Comments

Section divider comments (like `# ===== SECTION =====`) are acceptable for major functional blocks but should be used sparingly:

```python
def relevant_facts(state):
    logger.debug("--- RELEVANT FACTS ---")
    # ... implementation
```

## Code Structure

### Function and Variable Names

- Use descriptive names that clearly indicate purpose
- Prefer explicit over implicit naming
- Use `snake_case` for functions and variables
- Use `UPPER_CASE` for constants

```python
# Good
def extract_choice_of_law_section(state):
    jurisdiction_name = state.get("jurisdiction")
    
# Avoid
def extract_col(s):
    j = s.get("jurisdiction")
```

### Imports

Group imports in the following order:
1. Standard library imports
2. Third-party library imports  
3. Local application imports

```python
import logging
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

import config
from prompts.prompt_selector import get_prompt_module
```

## Testing

- Write tests for new functionality
- Keep existing tests passing
- Use descriptive test names that explain what is being tested
- Tests may use print statements for debugging output

## Documentation

- Update documentation when changing public APIs
- Keep README files up to date
- Document complex algorithms and workflows
- Use docstrings for public functions and classes

## Examples

### Before (Too Much Noise)

```python
def col_issue(state):
    print("\n--- CHOICE OF LAW ISSUE ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    # get last col_section (string)
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    print(f"\nPrompting LLM with:\n{prompt}\n")
    # Get dynamic system prompt based on jurisdiction
    system_prompt = get_system_prompt_for_analysis(state)
    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    col_issue = _ensure_text(getattr(response, "content", ""))
    print(f"\nChoice of Law Issue:\n{col_issue}\n")
    # append col_issue
    state.setdefault("col_issue", []).append(col_issue)
    # return full updated lists
    return {"col_issue": state["col_issue"], "col_issue_time": issue_time}
```

### After (Clean and Clear)

```python
def col_issue(state):
    logger.debug("--- CHOICE OF LAW ISSUE ---")
    text = state["full_text"]
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    
    col_section = ""
    sections = state.get("col_section", [])
    if sections:
        col_section = sections[-1]
    
    logger.debug("Prompting LLM with: %s", prompt)
    system_prompt = get_system_prompt_for_analysis(state)
    response = config.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=prompt)])
    col_issue = _ensure_text(getattr(response, "content", ""))
    logger.debug("Choice of Law Issue: %s", col_issue)
    
    state.setdefault("col_issue", []).append(col_issue)
    return {"col_issue": state["col_issue"], "col_issue_time": issue_time}
```

## Summary

1. **Use logging instead of print statements** in application code
2. **Remove redundant comments** that just repeat what the code does
3. **Comment to explain why, not what** - let the code explain what it does
4. **Keep it simple and readable** - clear code needs fewer comments
