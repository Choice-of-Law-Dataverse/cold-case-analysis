# components/theme_classifier.py
"""
Theme classification components for the CoLD Case Analyzer.
"""

import streamlit as st

from utils.data_loaders import load_valid_themes


def handle_theme_editing(state, last_theme, valid_themes):
    """
    Handle the theme editing interface.

    Args:
        state: The current analysis state
        last_theme: The last classified theme
        valid_themes: List of valid theme options
    """
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

    # Get last theme from classification
    themes = state.get("classification", [])
    if not themes:
        return

    last_theme = themes[-1]

    # Auto-approve theme classification without scoring UI
    if not state.get("theme_first_score_submitted"):
        state["theme_first_score_submitted"] = True

    # Handle theme editing
    handle_theme_editing(state, last_theme, valid_themes)
