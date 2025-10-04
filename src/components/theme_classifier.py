# components/theme_classifier.py
"""
Theme classification components for the CoLD Case Analyzer.
"""
import streamlit as st

from utils.data_loaders import load_valid_themes
from utils.state_manager import save_state_to_storage


def display_theme_classification(state):
    """
    Display the theme classification results.

    Args:
        state: The current analysis state
    """
    themes = state.get("classification", [])
    if themes:
        last_theme = themes[-1]
        st.markdown("**Themes:**")
        st.markdown(f"<div class='machine-message'>{last_theme}</div>", unsafe_allow_html=True)
        return last_theme
    return None


def handle_theme_scoring(state):
    """
    Handle the theme scoring interface.

    Args:
        state: The current analysis state

    Returns:
        bool: True if scoring is complete
    """
    if not state.get("theme_first_score_submitted"):
        score = st.slider(
            "Evaluate these themes (0-100):",
            min_value=0,
            max_value=100,
            value=100,
            step=1,
            key="theme_first_score_input"
        )
        if st.button("Submit Theme Score", key="submit_theme_score"):
            state["theme_first_score"] = score
            state["theme_first_score_submitted"] = True
            save_state_to_storage(state)
            st.rerun()
        return False
    else:
        score = state.get("theme_first_score", 0)
        st.markdown("**Your score for themes:**")
        st.markdown(f"<div class='user-message'>Score: {score}</div>", unsafe_allow_html=True)
        return True


def handle_theme_editing(state, last_theme, valid_themes):
    """
    Handle the theme editing interface.

    Args:
        state: The current analysis state
        last_theme: The last classified theme
        valid_themes: List of valid theme options
    """
    if not state.get("theme_done"):
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
            "Adjust themes:",
            options=valid_themes,
            default=filtered_defaults,
            key="theme_select"
        )

        if st.button("Submit Final Themes"):
            if selected:
                new_sel = ", ".join(selected)
                state.setdefault("classification", []).append(new_sel)
                state["theme_done"] = True
                state["analysis_ready"] = True
                state["analysis_step"] = 0
                save_state_to_storage(state)
                st.rerun()
            else:
                st.warning("Select at least one theme before proceeding.")


def display_final_themes(state):
    """
    Display the final edited themes.

    Args:
        state: The current analysis state
    """
    if state.get("theme_done"):
        final = state.get("classification", [])[-1]
        st.markdown("**Final Themes:**")
        st.markdown(f"<div class='user-message'>{final}</div>", unsafe_allow_html=True)


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
