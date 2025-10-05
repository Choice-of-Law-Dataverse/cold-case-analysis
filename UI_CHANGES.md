# UI Changes - Confidence Display

## Overview
Every editable textarea in the analysis workflow now displays a confidence chip showing the AI's confidence level in that particular analysis step.

## Confidence Chip Design

### Visual Appearance
- **Location**: Top-right corner next to the section title
- **Color**: Purple background (#9b4dca)
- **Icon**: 🔍 magnifying glass emoji
- **Text**: Confidence percentage (e.g., "🔍 87%")
- **Style**: Rounded pill/chip button
- **Hover**: Darker purple (#7d3ca8)

### Layout Pattern
```
┌─────────────────────────────────────────────────────────────┐
│ Section Title                              [🔍 87%]          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Editable text area with analysis content             │   │
│  │                                                       │   │
│  │ User can edit the text here...                       │   │
│  │                                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Modal Dialog (Click on Chip)

When user clicks the confidence chip, a modal dialog appears:

```
┌─────────────────────────────────────────────────┐
│  Confidence Level: 87%                      [X] │
├─────────────────────────────────────────────────┤
│                                                  │
│  Confidence Score: 87%                          │
│  [████████████████████░░░] (progress bar)       │
│                                                  │
│  ─────────────────────────────────────────────  │
│                                                  │
│  Reasoning:                                     │
│                                                  │
│  High confidence because the text clearly       │
│  identifies Switzerland as the jurisdiction     │
│  through multiple references to Swiss law       │
│  and the Swiss Federal Supreme Court.           │
│                                                  │
│                                                  │
│                     [Close]                     │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Where Confidence Chips Appear

### 1. Jurisdiction Detection
- **Step**: After detecting jurisdiction
- **Location**: Next to "Jurisdiction Detection Results"
- **Example**: Shows confidence in jurisdiction identification

### 2. Choice of Law Extraction
- **Step**: When editing CoL section
- **Location**: Next to "Edit extracted Choice of Law section"
- **Example**: Shows confidence in CoL section extraction

### 3. Theme Classification
- **Step**: When selecting themes
- **Location**: Next to "Theme Classification"
- **Example**: Shows confidence in theme categorization

### 4. Analysis Steps (All 7 Steps)
Each analysis step shows a confidence chip:
- **Relevant Facts** - Confidence in factual extraction
- **PIL Provisions** - Confidence in identifying legal provisions
- **Choice of Law Issue(s)** - Confidence in issue identification
- **Court's Position** - Confidence in analyzing court's reasoning
- **Obiter Dicta** (Common Law only) - Confidence in identifying obiter
- **Dissenting Opinions** (Common Law only) - Confidence in dissent analysis
- **Abstract** - Confidence in abstract quality

## CSS Customization

The purple chip styling is defined in `src/components/confidence_display.py`:

```css
/* Confidence chip styling */
div[data-testid="column"] button[kind="secondary"] {
    background-color: #9b4dca !important;  /* Purple */
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 4px 12px !important;
    font-size: 0.85em !important;
    font-weight: 500 !important;
    cursor: pointer !important;
}

div[data-testid="column"] button[kind="secondary"]:hover {
    background-color: #7d3ca8 !important;  /* Darker purple on hover */
}
```

## User Interaction Flow

1. User sees section with confidence chip
2. User notes confidence percentage (e.g., 87%)
3. If user wants more details:
   - Click on chip
   - Modal opens
   - Read detailed reasoning
   - Click "Close" or click outside modal
4. User can then:
   - Edit the text if needed
   - Accept as-is if satisfied
   - Proceed to next step

## Implementation Notes

- Confidence chips are non-blocking - they don't interfere with workflow
- Modal is dismissable - user can close it anytime
- Confidence data is stored in session state
- All chips use consistent styling
- Responsive layout works on different screen sizes

## Example Confidence Levels

Typical confidence ranges:
- **0.90-1.00 (90-100%)**: Very high confidence, clear indicators
- **0.75-0.89 (75-89%)**: High confidence, strong evidence
- **0.60-0.74 (60-74%)**: Moderate confidence, some ambiguity
- **0.00-0.59 (0-59%)**: Lower confidence, uncertain or complex case

## Accessibility

- Chips are keyboard accessible
- Modal can be closed with Esc key
- Color contrast meets WCAG standards (white text on purple)
- Icon provides visual cue in addition to text
