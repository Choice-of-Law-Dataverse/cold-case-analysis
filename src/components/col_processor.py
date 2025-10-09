# components/col_processor.py
"""
Choice of Law section processing components.
"""

import os

import streamlit as st

from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state


def display_jurisdiction_info():
    """
    Display jurisdiction information if available.
    """
    col_state = st.session_state.col_state
    precise_jurisdiction = col_state.get("precise_jurisdiction")
    jurisdiction = col_state.get("jurisdiction")
    jurisdiction_code = col_state.get("jurisdiction_code")

    if precise_jurisdiction or jurisdiction:
        st.subheader("Jurisdiction")

        if precise_jurisdiction and precise_jurisdiction != "Unknown":
            jurisdiction_display = f"{precise_jurisdiction}"
            if jurisdiction_code:
                jurisdiction_display += f" ({jurisdiction_code})"

            st.badge(jurisdiction_display)

        if jurisdiction:
            st.badge(jurisdiction)


def display_col_extractions():
    """
    Display the history of COL extractions and feedback.
    """
    col_state = st.session_state.col_state
    if not col_state.get("col_first_score_submitted"):
        col_state["col_first_score_submitted"] = True


def handle_col_feedback_phase():
    """
    Handle the COL feedback and editing phase.
    """
    col_state = st.session_state.col_state
    if not col_state.get("col_ready_edit"):
        col_state["col_ready_edit"] = True

    render_edit_section()


def render_feedback_input():
    """
    Render the feedback input interface.
    """
    col_state = st.session_state.col_state
    feedback = st.text_area(
        "Enter feedback to improve the Choice of Law Section:",
        height=150,
        key="col_feedback",
        help="Provide feedback to refine the extracted Choice of Law Section.",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Feedback", key="submit_col_feedback"):
            if feedback:
                col_state["col_section_feedback"].append(feedback)

                model = col_state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

                result = extract_col_section(
                    text=col_state["full_text"],
                    legal_system=col_state.get("jurisdiction", "Civil-law jurisdiction"),
                    jurisdiction=col_state.get("precise_jurisdiction"),
                    model=model,
                )

                col_state.setdefault("col_section", []).append(result.col_sections)
                col_state.setdefault("col_section_confidence", []).append(result.confidence)
                col_state.setdefault("col_section_reasoning", []).append(result.reasoning)

                st.rerun()
            else:
                st.warning("Please enter feedback to improve the extraction.")

    with col2:
        if st.button("Proceed to Edit Section", key="proceed_col_edit"):
            col_state["col_ready_edit"] = True
            st.rerun()


def render_edit_section():
    """
    Render the edit section interface.
    """
    col_state = st.session_state.col_state
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip

    # Add CSS for confidence chips
    add_confidence_chip_css()

    last_extraction = col_state.get("col_section", [""])[-1]
    confidence = col_state.get("col_section_confidence", [])[-1] if col_state.get("col_section_confidence") else None
    reasoning = (
        col_state.get("col_section_reasoning", [""])[-1] if col_state.get("col_section_reasoning") else "No reasoning available"
    )

    with st.container(horizontal=True):
        st.markdown("### Edit extracted Choice of Law section")
        if confidence:
            # Use a more unique key to avoid widget conflicts
            chip_key = f"col_extraction_{hash(reasoning) % 10000}"
            render_confidence_chip(confidence, reasoning, chip_key)

    # Use custom CSS to set height with min and max
    st.markdown(
        """
    <style>
    div[data-testid="stTextArea"] textarea[aria-label="Edit extracted Choice of Law section:"] {
        min-height: 400px !important;
        max-height: 66vh !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    edited_extraction = st.text_area(
        "Edit extracted Choice of Law section:",
        value=last_extraction,
        height=600,
        key="col_edit_section",
        label_visibility="collapsed",
        help="Modify the extracted section before proceeding to theme classification",
        disabled=col_state.get("col_done", False),
    )

    print_state("\n\n\nCurrent CoLD State\n\n", col_state)

    if not col_state.get("col_done"):
        if st.button("Submit and Classify", key="submit_and_classify_btn"):
            if edited_extraction:
                col_state["col_section"].append(edited_extraction)
                col_state["col_done"] = True
                col_state["classification"] = []

                from tools.theme_classifier import theme_classification_node

                model = col_state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

                result = theme_classification_node(
                    text=col_state["full_text"],
                    col_section=edited_extraction,
                    legal_system=col_state.get("jurisdiction", "Civil-law jurisdiction"),
                    jurisdiction=col_state.get("precise_jurisdiction"),
                    model=model,
                )

                cls_str = ", ".join(str(item) for item in result.themes)
                col_state.setdefault("classification", []).append(cls_str)
                col_state.setdefault("classification_confidence", []).append(result.confidence)
                col_state.setdefault("classification_reasoning", []).append(result.reasoning)

                print_state("\n\n\nUpdated CoLD State after classification\n\n", col_state)
                st.rerun()
            else:
                st.warning("Please edit the extracted section before proceeding.")


def render_col_processing():
    """
    Render the complete COL processing interface.
    """
    col_state = st.session_state.col_state

    display_col_extractions()

    if not col_state.get("col_done"):
        handle_col_feedback_phase()
