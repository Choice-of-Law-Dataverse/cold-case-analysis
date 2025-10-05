"""UI components for displaying confidence levels with reasoning modals."""

from typing import Literal

import streamlit as st


def render_confidence_chip(confidence: Literal["low", "medium", "high"], reasoning: str, key_suffix: str = ""):
    """
    Render a confidence chip with purple background that opens a modal on click.

    Args:
        confidence: Confidence level: 'low', 'medium', or 'high'
        reasoning: Explanation text to show in modal
        key_suffix: Unique suffix for component keys
    """
    # Create a unique key for the modal
    modal_key = f"confidence_modal_{key_suffix}"

    # Create the chip as a button with custom styling
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        # Use a button that looks like a chip with confidence level text
        chip_clicked = st.button(
            f"🔍 {confidence.upper()}",
            key=f"confidence_chip_{key_suffix}",
            help="Click to see reasoning",
            use_container_width=True
        )

    # Store modal state
    if chip_clicked:
        st.session_state[modal_key] = True

    # Display modal if activated
    if st.session_state.get(modal_key, False):
        render_confidence_modal(confidence, reasoning, modal_key)


def render_confidence_modal(confidence: Literal["low", "medium", "high"], reasoning: str, modal_key: str):
    """
    Render a modal dialog with confidence details.

    Args:
        confidence: Confidence level: 'low', 'medium', or 'high'
        reasoning: Explanation text
        modal_key: Key for tracking modal state
    """
    # Map confidence levels to progress values
    confidence_map = {"low": 0.33, "medium": 0.66, "high": 1.0}
    progress_value = confidence_map.get(confidence.lower(), 0.5)

    # Create modal using st.dialog (Streamlit 1.50+)
    @st.dialog(f"Confidence Level: {confidence.upper()}")
    def show_modal():
        st.markdown(f"**Confidence Level:** {confidence.upper()}")
        st.progress(progress_value)
        st.markdown("---")
        st.markdown("**Reasoning:**")
        st.markdown(reasoning)

        if st.button("Close", key=f"close_modal_{modal_key}"):
            st.session_state[modal_key] = False
            st.rerun()

    show_modal()


def add_confidence_chip_css():
    """Add custom CSS for confidence chips with purple background."""
    st.markdown(
        """
        <style>
        /* Confidence chip styling */
        div[data-testid="column"] button[kind="secondary"] {
            background-color: #9b4dca !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 4px 12px !important;
            font-size: 0.85em !important;
            font-weight: 500 !important;
            cursor: pointer !important;
        }

        div[data-testid="column"] button[kind="secondary"]:hover {
            background-color: #7d3ca8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
