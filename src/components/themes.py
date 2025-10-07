# components/theme_classifier.py
"""
Theme classification components for the CoLD Case Analyzer.
"""

import streamlit as st

from utils.data_loaders import load_valid_themes


def display_theme_classification():
    """
    Display the theme classification results.
    """
    state = st.session_state.col_state
    themes = state.get("classification", [])
    if themes:
        last_theme = themes[-1]
        return last_theme
    return None


def handle_theme_editing(last_theme, valid_themes):
    """
    Handle the theme editing interface.

    Args:
        last_theme: The last classified theme
        valid_themes: List of valid theme options
    """
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip

    state = st.session_state.col_state
    add_confidence_chip_css()

    confidence = state.get("classification_confidence", [])[-1] if state.get("classification_confidence") else None
    reasoning = (
        state.get("classification_reasoning", [""])[-1] if state.get("classification_reasoning") else "No reasoning available"
    )

    with st.container(horizontal=True):
        st.subheader("Themes")
        if confidence:
            chip_key = f"theme_classification_{hash(reasoning) % 10000}"
            render_confidence_chip(confidence, reasoning, chip_key)

    default_sel = [t.strip() for t in last_theme.split(",") if t.strip()]

    theme_mapping = {theme.lower(): theme for theme in valid_themes}

    filtered_defaults = []
    for theme in default_sel:
        if theme in valid_themes:
            filtered_defaults.append(theme)
        elif theme.lower() in theme_mapping:
            filtered_defaults.append(theme_mapping[theme.lower()])

    if "theme_done" in state and state["theme_done"]:
        for theme in filtered_defaults:
            st.badge(theme)
    else:
        selected = st.multiselect(
            "Select themes:",
            options=valid_themes,
            default=filtered_defaults,
            key="theme_select",
            disabled=state.get("theme_done", False),
            label_visibility="collapsed",
        )

        if st.button("Submit Final Themes", key="submit_final_themes"):
            if selected:
                new_sel = ", ".join(selected)
                state.setdefault("classification", []).append(new_sel)
                state["theme_done"] = True
                state["analysis_ready"] = True
                state["analysis_step"] = 0
                st.rerun()
            else:
                st.warning("Select at least one theme before proceeding.")


def render_theme_classification():
    """
    Render the complete theme classification interface.
    """
    state = st.session_state.col_state
    if not state.get("col_done"):
        return

    valid_themes = load_valid_themes()
    valid_themes.append("NA")

    last_theme = display_theme_classification()

    if last_theme:
        if not state.get("theme_first_score_submitted"):
            state["theme_first_score_submitted"] = True

        handle_theme_editing(last_theme, valid_themes)
