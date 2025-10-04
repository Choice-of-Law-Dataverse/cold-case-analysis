# components/col_processor.py
"""
Choice of Law section processing components.
"""

import streamlit as st

from tools.col_extractor import extract_col_section
from utils.debug_print_state import print_state


def display_jurisdiction_info(col_state):
    """
    Display jurisdiction information if available.

    Args:
        col_state: The current analysis state
    """
    precise_jurisdiction = col_state.get("precise_jurisdiction")
    jurisdiction = col_state.get("jurisdiction")
    jurisdiction_code = col_state.get("jurisdiction_code")

    if precise_jurisdiction or jurisdiction:
        st.markdown("### Jurisdiction")
        col1, col2 = st.columns([2, 1])

        with col1:
            if precise_jurisdiction and precise_jurisdiction != "Unknown":
                jurisdiction_display = f"{precise_jurisdiction}"
                if jurisdiction_code:
                    jurisdiction_display += f" ({jurisdiction_code})"
                st.markdown(f"**Specific Jurisdiction:** {jurisdiction_display}")

            if jurisdiction:
                st.markdown(f"**Legal System:** {jurisdiction}")

        st.markdown("---")


def display_case_info(col_state):
    """
    Display case citation without the full text.

    Args:
        col_state: The current analysis state
    """
    citation = col_state.get("case_citation")
    if citation:
        st.markdown("**Case Citation:**")
        st.markdown(f"<div class='user-message'>{citation}</div>", unsafe_allow_html=True)

    display_jurisdiction_info(col_state)


def display_col_extractions(col_state):
    """
    Display the history of COL extractions and feedback.

    Args:
        col_state: The current analysis state
    """
    # Handle scoring for first extraction
    handle_first_extraction_scoring(col_state)


def handle_first_extraction_scoring(col_state):
    """
    Auto-approve the first COL extraction without scoring UI.

    Args:
        col_state: The current analysis state
    """
    # Automatically mark as submitted without user interaction
    if not col_state.get("col_first_score_submitted"):
        col_state["col_first_score_submitted"] = True


def handle_col_feedback_phase(col_state):
    """
    Handle the COL feedback and editing phase.

    Args:
        col_state: The current analysis state
    """
    # Auto-approve first extraction, skip to editing
    if not col_state.get("col_ready_edit"):
        col_state["col_ready_edit"] = True

    render_edit_section(col_state)


def render_feedback_input(col_state):
    """
    Render the feedback input interface.

    Args:
        col_state: The current analysis state
    """
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
                result = extract_col_section(col_state)
                col_state.update(result)
                st.rerun()
            else:
                st.warning("Please enter feedback to improve the extraction.")

    with col2:
        if st.button("Proceed to Edit Section", key="proceed_col_edit"):
            col_state["col_ready_edit"] = True
            st.rerun()


def render_edit_section(col_state):
    """
    Render the edit section interface.

    Args:
        col_state: The current analysis state
    """
    last_extraction = col_state.get("col_section", [""])[-1]

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
        help="Modify the extracted section before proceeding to theme classification",
        disabled=col_state.get("col_done", False),
    )

    print_state("\n\n\nCurrent CoLD State\n\n", col_state)

    if not col_state.get("col_done"):
        if st.button("Submit and Classify"):
            if edited_extraction:
                # Save edited extraction and run classification
                col_state["col_section"].append(edited_extraction)
                col_state["col_done"] = True
                col_state["classification"] = []
                col_state["theme_feedback"] = []
                col_state["theme_eval_iter"] = 0

                from tools.themes_classifier import theme_classification_node
                from utils.progress_banner import hide_progress_banner, show_progress_banner

                # Show progress banner while classifying
                show_progress_banner("Identifying themes...")

                init_result = theme_classification_node(col_state)
                col_state.update(init_result)

                print_state("\n\n\nUpdated CoLD State after classification\n\n", col_state)

                # Clear the progress banner
                hide_progress_banner()
                st.rerun()
            else:
                st.warning("Please edit the extracted section before proceeding.")


def render_col_processing(col_state):
    """
    Render the complete COL processing interface.

    Args:
        col_state: The current analysis state
    """
    # Display case information
    display_case_info(col_state)

    # Display extraction history
    display_col_extractions(col_state)

    # Always show the edit section (even after col_done) so user can see extracted text
    # Handle feedback and editing if COL not done
    if not col_state.get("col_done"):
        handle_col_feedback_phase(col_state)
    else:
        # Show the textarea in read-only mode after classification
        render_edit_section(col_state)
