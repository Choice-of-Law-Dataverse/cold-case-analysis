# Dynamic System Prompts Feature

## Overview

The dynamic system prompts feature enhances the CoLD Case Analyzer by providing jurisdiction-specific AI instructions based on the detected jurisdiction and legal system type. This improves the accuracy and relevance of legal analysis by giving the AI model contextual information about the specific legal framework governing the case.

## How It Works

### 1. Jurisdiction Detection
- When a court decision is analyzed, the system first detects the specific jurisdiction (e.g., "Germany", "United States of America", "India")
- The legal system type is also classified (e.g., "Civil-law jurisdiction", "Common-law jurisdiction")

### 2. System Prompt Generation
- Based on the detected jurisdiction, the system generates a customized instruction set for the AI model
- The base system prompt includes general instructions about:
  - Being precise and analytical
  - Basing analysis strictly on provided court decision text
  - Providing output in English (with exceptions for exact quotes)
  - Focusing on private international law elements

### 3. Jurisdiction-Specific Context
- If a jurisdiction summary is available in `data/jurisdictions.csv`, it gets added to the system prompt
- This provides the AI with relevant context about the private international law framework in that jurisdiction
- Examples of context include:
  - Applicable legal codes and regulations (e.g., Rome I Regulation for EU countries)
  - Party autonomy principles
  - Choice of law methodologies
  - Default rules when no choice is made

## Benefits

1. **Improved Accuracy**: AI models perform better when given relevant contextual information
2. **Legal System Awareness**: The AI understands whether it's analyzing a civil law or common law decision
3. **Jurisdiction-Specific Knowledge**: Access to specialized legal framework information for each country/jurisdiction
4. **Consistent Analysis**: Standardized approach to different legal traditions
5. **Language Handling**: Clear instructions for multilingual analysis with English output

## Technical Implementation

### Files Modified
- `utils/system_prompt_generator.py`: Core system prompt generation logic
- `tools/case_analyzer.py`: Updated to use dynamic prompts for analysis functions
- `tools/theme_classifier.py`: Updated for theme classification
- `tools/col_extractor.py`: Updated for choice of law section extraction
- `components/sidebar.py`: Added preview functionality

### Key Functions
- `generate_jurisdiction_specific_prompt()`: Creates customized system prompts
- `load_jurisdiction_summaries()`: Loads jurisdiction data from CSV
- `get_system_prompt_for_analysis()`: Extracts jurisdiction info from analysis state

### Data Source
The jurisdiction summaries are sourced from `data/jurisdictions.csv` which contains:
- Jurisdiction names (e.g., "Germany", "France", "Brazil")
- Alpha-3 country codes
- Detailed summaries of private international law frameworks

## Usage Examples

### Basic System Prompt (No Jurisdiction Detected)
```
You are an expert in private international law and choice of law analysis.

CORE INSTRUCTIONS:
- Be precise and analytical in your responses
- Base all analysis STRICTLY on the information provided in the court decision text
- Do not infer, assume, or add information not explicitly stated in the source material
...
```

### Enhanced System Prompt (Germany Detected)
```
You are an expert in private international law and choice of law analysis.

CORE INSTRUCTIONS:
- Be precise and analytical in your responses
...

JURISDICTION-SPECIFIC CONTEXT:
This case originates from Germany. The following provides relevant context about the private international law framework in this jurisdiction:

The Rome I Regulation is the primary legal framework for determining the applicable law in international commercial contracts within the European Union, excluding Denmark. It supersedes the 1980 Rome Convention and applies to contracts concluded after December 17, 2009...

Use this contextual information to inform your analysis, but remember to base your conclusions on what is actually stated in the court decision text.

LEGAL SYSTEM CONTEXT:
This decision comes from a civil law legal system. Consider the typical approaches and methodologies of this legal tradition in your analysis.
```

## Testing and Debugging

### Sidebar Preview
- Logged-in users can preview the generated system prompt in the sidebar
- Shows current jurisdiction and legal system type
- Displays the full system prompt that will be used for AI analysis

### Manual Testing
The system includes testing utilities in `utils/test_system_prompts.py` for:
- Manual system prompt generation testing
- Viewing all available jurisdictions with summaries
- Searching and filtering jurisdictions

## Future Enhancements

1. **More Jurisdictions**: Add summaries for additional jurisdictions
2. **Court-Specific Context**: Add context for specific courts within jurisdictions  
3. **Legal Area Specialization**: Customize prompts for different areas of law
4. **Dynamic Learning**: Update jurisdiction summaries based on analysis results
5. **Multi-language Support**: Enhanced instructions for non-English court decisions

## Configuration

### Adding New Jurisdiction Summaries
1. Edit `data/jurisdictions.csv`
2. Add the jurisdiction name in the "Name" column
3. Add a comprehensive summary in the "Jurisdiction Summary" column
4. The system will automatically use the new summary

### Customizing Base Prompt
Edit the `generate_base_system_prompt()` function in `utils/system_prompt_generator.py` to modify the core instructions sent to all AI models.

## Error Handling

- If `jurisdictions.csv` cannot be loaded, the system defaults to the base prompt
- Missing jurisdiction summaries are handled gracefully
- Invalid jurisdiction names don't break the system
- Fallbacks ensure analysis can continue even with missing data
