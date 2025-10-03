# PIL Provisions Handler Documentation

## Overview
The PIL Provisions Handler provides user-friendly display and editing of Private International Law provisions, converting technical markdown formatting into readable content.

## Features

### 1. Automatic Format Detection
- Handles simple list formats: `["provision 1", "provision 2"]`  
- Handles complex structured formats with sections like:
  - **Judicial Precedents**
  - **Textbooks/Academic Sources** 
  - **Statutory Provisions**
  - **Legal Principles**
  - **Summary**

### 2. User-Friendly Display
- Converts markdown formatting to clean bullet points
- Removes technical syntax like `\n`, `**`, etc.
- Organizes content into clear sections
- Handles multi-line items properly

### 3. Smart Editing Interface
- Provides editing instructions to users
- Maintains compatibility with the underlying data structure
- Supports both simple and complex formats
- Preserves user edits in the session state

## Example Transformation

**Input (technical format):**
```
['**Judicial Precedents:**\n- Shamil Bank of Bahrain EC v Beximco Pharmaceuticals Ltd\n\n**Textbooks/Academic Sources:**\n- Dicey, Morris & Collins: Used extensively to interpret...']
```

**Output (user-friendly format):**
```
**Judicial Precedents:**
• Shamil Bank of Bahrain EC v Beximco Pharmaceuticals Ltd

**Textbooks/Academic Sources:**
• Dicey, Morris & Collins: Used extensively to interpret the conflict rules under the Rome Convention, particularly regarding the recognition of foreign laws such as Jewish law and rules of incorporation, and to explain how law of a country is the relevant legal system in conflict of laws.
• Professor Burrows: Cited to discuss the modern approach to rescission for duress...
```

## Usage in Analysis Workflow

The handler is automatically used for the `pil_provisions` step:

1. **Display**: Raw PIL data is parsed and formatted for user-friendly display
2. **Editing**: Users can edit with simple bullet points and section headers
3. **Storage**: Edited content is converted back to compatible format for storage

## Technical Implementation

### Key Functions:
- `parse_pil_provisions()`: Parses different input formats into structured data
- `format_pil_for_display()`: Formats structured data for user display  
- `display_pil_provisions()`: Main display function with format detection
- `handle_pil_provisions_editing()`: Editing interface with instructions
- `update_pil_provisions_state()`: Updates state with edited content

### Integration Points:
- `analysis_workflow.py`: Special handling in `execute_analysis_step()` and `handle_step_editing()`
- Maintains backward compatibility with existing data structures
- Preserves chat history with formatted content
