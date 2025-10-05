# components/theme_classifier.py
"""
Theme classification components for the CoLD Case Analyzer.
"""

import streamlit as st

from utils.data_loaders import load_valid_themes


def display_theme_classification(state):
    """
    Display the theme classification results.

    Args:
        state: The current analysis state
    """
    # Don't display redundant theme output - just let the multiselect handle it
    themes = state.get("classification", [])
    if themes:
        last_theme = themes[-1]
        return last_theme
    return None


def handle_theme_scoring(state):
    """
    Auto-approve theme classification without scoring UI.

    Args:
        state: The current analysis state

    Returns:
        bool: True (always complete)
    """
    # Automatically mark as submitted without user interaction
    if not state.get("theme_first_score_submitted"):
        state["theme_first_score_submitted"] = True
    return True


def handle_theme_editing(state, last_theme, valid_themes):
    """
    Handle the theme editing interface.

    Args:
        state: The current analysis state
        last_theme: The last classified theme
        valid_themes: List of valid theme options
    """
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip

    # Add CSS for confidence chips
    add_confidence_chip_css()

    # Get confidence and reasoning
    confidence = state.get("classification_confidence", [0.0])[-1] if state.get("classification_confidence") else 0.0
    reasoning = state.get("classification_reasoning", [""])[-1] if state.get("classification_reasoning") else "No reasoning available"

    # Display title with confidence chip
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown("### Theme Classification")
    with col2:
        if confidence > 0:
            render_confidence_chip(confidence, reasoning, "theme_classification")

    # Parse default selection and filter to only include valid themes
    default_sel = [t.strip() for t in last_theme.split(",") if t.strip()]

    # Create a case-insensitive mapping for matching
    theme_mapping = {theme.lower(): theme for theme in valid_themes}

    # Only include defaults that exist in valid_themes (case-insensitive matching)
    filtered_defaults = []
    for theme in default_sel:
        if theme in valid_themes:
            filtered_defaults.append(theme)
        elif theme.lower() in theme_mapping:
            # Use the correctly cased version from valid_themes
            filtered_defaults.append(theme_mapping[theme.lower()])

    selected = st.multiselect(
        "Themes:",
        options=valid_themes,
        default=filtered_defaults,
        key="theme_select",
        disabled=state.get("theme_done", False),
    )

    if not state.get("theme_done"):
        if st.button("Submit Final Themes"):
            if selected:
                new_sel = ", ".join(selected)
                state.setdefault("classification", []).append(new_sel)
                state["theme_done"] = True
                state["analysis_ready"] = True
                state["analysis_step"] = 0
                st.rerun()
            else:
                st.warning("Select at least one theme before proceeding.")


def display_final_themes(state):
    """
    Display the final edited themes - removed as redundant.

    Args:
        state: The current analysis state
    """
    # No longer display - multiselect shows the themes
    pass


def render_theme_classification(state):
    """
    Render the complete theme classification interface.

    Args:
        state: The current analysis state
    """
    if not state.get("col_done"):
        return

    # Load valid themes
    valid_themes = load_valid_themes()
    # Add "NA" option to the list
    valid_themes.append("NA")

    # Display classification results
    last_theme = display_theme_classification(state)

    if last_theme:
        # Handle scoring
        scoring_complete = handle_theme_scoring(state)

        if scoring_complete:
            # Handle theme editing
            handle_theme_editing(state, last_theme, valid_themes)

    # Display final themes if done
    display_final_themes(state)
