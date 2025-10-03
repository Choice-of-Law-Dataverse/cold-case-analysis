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
        st.markdown("### Identified Jurisdiction")
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
    Display case citation and full text.

    Args:
        col_state: The current analysis state
    """
    citation = col_state.get("case_citation")
    if citation:
        st.markdown("**Case Citation:**")
        st.markdown(f"<div class='user-message'>{citation}</div>", unsafe_allow_html=True)

    display_jurisdiction_info(col_state)

    # Display the full court decision text at the top as a user message
    st.markdown("**Your Input (Court Decision Text):**")
    st.markdown(f"<div class='user-message'>{col_state['full_text']}</div>", unsafe_allow_html=True)


def display_col_extractions(col_state):
    """
    Display the history of COL extractions and feedback.

    Args:
        col_state: The current analysis state
    """
    extractions = col_state.get("col_section", [])
    feedbacks = col_state.get("col_section_feedback", [])

    for i, col in enumerate(extractions):
        # Show all extractions as machine messages, but if final edited extraction has been submitted, show it as a user message
        if i == len(extractions) - 1 and col_state.get("col_done"):
            st.markdown("**Your Edited Choice of Law Section:**")
            st.markdown(f"<div class='user-message'>{col}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Choice of Law Section Extraction {i+1}:**")
            st.markdown(f"<div class='machine-message'>{col}</div>", unsafe_allow_html=True)

        # Handle scoring for first extraction
        if i == 0:
            handle_first_extraction_scoring(col_state)

        # Display feedback if available
        if i < len(feedbacks):
            st.markdown("**User:**")
            st.markdown(f"<div class='user-message'>{feedbacks[i]}</div>", unsafe_allow_html=True)


def handle_first_extraction_scoring(col_state):
    """
    Handle scoring for the first COL extraction.

    Args:
        col_state: The current analysis state
    """
    from utils.state_manager import is_processing
    
    if not col_state.get("col_first_score_submitted"):
        # Score input restricted to 0–100
        score_input = st.slider(
            "Evaluate this first extraction (0-100):",
            min_value=0,
            max_value=100,
            value=100,
            step=1,
            help="Provide a score for the quality of the first extraction",
            key="col_first_score_input",
            disabled=is_processing()
        )
        if st.button("Submit Score", key="submit_col_score", disabled=is_processing()):
            col_state["col_first_score"] = score_input
            col_state["col_first_score_submitted"] = True
            st.rerun()
    else:
        score = col_state.get("col_first_score", 0)
        st.markdown("**Your score for extraction 1:**")
        st.markdown(f"<div class='user-message'>Score: {score}</div>", unsafe_allow_html=True)


def handle_col_feedback_phase(col_state):
    """
    Handle the COL feedback and editing phase.

    Args:
        col_state: The current analysis state
    """
    if not col_state.get("col_ready_edit"):
        # Only allow feedback after initial score
        if not col_state.get("col_first_score_submitted"):
            st.info("Please submit the extraction score before providing feedback.")
        else:
            render_feedback_input(col_state)
    else:
        render_edit_section(col_state)


def render_feedback_input(col_state):
    """
    Render the feedback input interface.

    Args:
        col_state: The current analysis state
    """
    from utils.state_manager import is_processing, set_processing
    
    feedback = st.text_area(
        "Enter feedback to improve the Choice of Law Section:",
        height=150,
        key="col_feedback",
        help="Provide feedback to refine the extracted Choice of Law Section.",
        disabled=is_processing()
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Feedback", key="submit_col_feedback", disabled=is_processing()):
            if feedback:
                set_processing(True)
                with st.spinner("Processing feedback and re-extracting..."):
                    col_state["col_section_feedback"].append(feedback)
                    result = extract_col_section(col_state)
                    col_state.update(result)
                set_processing(False)
                st.rerun()
            else:
                st.warning("Please enter feedback to improve the extraction.")

    with col2:
        if st.button("Proceed to Edit Section", key="proceed_col_edit", disabled=is_processing()):
            col_state["col_ready_edit"] = True
            st.rerun()


def render_edit_section(col_state):
    """
    Render the edit section interface.

    Args:
        col_state: The current analysis state
    """
    from utils.state_manager import is_processing, set_processing
    
    last_extraction = col_state.get("col_section", [""])[-1]
    edited_extraction = st.text_area(
        "Edit extracted Choice of Law section:",
        value=last_extraction,
        height=200,
        key="col_edit_section",
        help="Modify the extracted section before proceeding to theme classification",
        disabled=is_processing()
    )

    print_state("\n\n\nCurrent CoLD State\n\n", col_state)

    if st.button("Submit and Classify", disabled=is_processing()):
        if edited_extraction:
            set_processing(True)
            with st.spinner("Classifying themes..."):
                # Save edited extraction and run classification
                col_state["col_section"].append(edited_extraction)
                col_state["col_done"] = True
                col_state["classification"] = []
                col_state["theme_feedback"] = []
                col_state["theme_eval_iter"] = 0

                from tools.themes_classifier import theme_classification_node
                init_result = theme_classification_node(col_state)
                col_state.update(init_result)

                print_state("\n\n\nUpdated CoLD State after classification\n\n", col_state)
            set_processing(False)
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

    # Handle feedback and editing if COL not done
    if not col_state.get("col_done"):
        handle_col_feedback_phase(col_state)
