# components/analysis_workflow.py
"""
Analysis workflow components for the CoLD Case Analyzer.
"""
import streamlit as st

from components.database import save_to_db
from components.pil_provisions_handler import display_pil_provisions, handle_pil_provisions_editing, update_pil_provisions_state
from utils.debug_print_state import print_state


def get_step_display_name(step_name, state):
    """
    Get the proper display name for an analysis step based on jurisdiction.
    
    Args:
        step_name: The internal step name (e.g., "relevant_facts")
        state: The current analysis state (to determine jurisdiction)
        
    Returns:
        str: The formatted display name for the step
    """
    jurisdiction = state.get("jurisdiction", "")
    is_common_law_or_indian = jurisdiction == "Common-law jurisdiction" or jurisdiction == "Indian jurisdiction"

    step_names = {
        "relevant_facts": "Relevant Facts",
        "pil_provisions": "Private International Law Sources",
        "col_issue": "Choice of Law Issue(s)",
        "courts_position": "Court's Position (Ratio Decidendi)" if is_common_law_or_indian else "Court's Position",
        "obiter_dicta": "Court's Position (Obiter Dicta)",
        "dissenting_opinions": "Dissenting Opinions",
        "abstract": "Abstract"
    }

    return step_names.get(step_name, step_name.replace("_", " ").title())


def display_analysis_history(state):
    """
    Display chronological chat history of analysis.
    
    Args:
        state: The current analysis state
    """
    for speaker, msg in state.get("chat_history", []):
        if speaker == "machine":
            # Separate step label and content if formatted as 'Step: content'
            if ": " in msg:
                step_label, content = msg.split(": ", 1)
                # Display step label in bold
                st.markdown(f"**{step_label}**")
                # Display content as machine message
                st.markdown(f"<div class='machine-message'>{content}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='machine-message'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='user-message'>{msg}</div>", unsafe_allow_html=True)


def display_completion_message(state):
    """
    Display the completion message and save to database.
    
    Args:
        state: The current analysis state
    """
    if state.get("analysis_done"):
        print("\n\n\nAnalysis completed, saving state to database...\n\n")
        save_to_db(state)
        st.markdown(
            "<div class='machine-message'>Thank you for using the CoLD Case Analyzer.<br>"
            "If you would like to find out more about the project, please visit "
            '<a href="https://cold.global" target="_blank">cold.global</a></div>',
            unsafe_allow_html=True
        )
        return True
    return False


def get_analysis_steps(state):
    """
    Get the analysis steps based on jurisdiction type.
    
    Args:
        state: The current analysis state
        
    Returns:
        list: List of (name, function) tuples for analysis steps
    """
    from tools.case_analyzer import (
        abstract,
        col_issue,
        courts_position,
        dissenting_opinions,
        obiter_dicta,
        pil_provisions,
        relevant_facts,
    )

    # Build base pipeline - abstract moved to end
    steps = [
        ("relevant_facts", relevant_facts),
        ("pil_provisions", pil_provisions),
        ("col_issue", col_issue),
        ("courts_position", courts_position)
    ]

    # Add extra steps for common-law decisions
    if state.get("jurisdiction") == "Common-law jurisdiction":
        steps.extend([
            ("obiter_dicta", obiter_dicta),
            ("dissenting_opinions", dissenting_opinions)
        ])

    # Add abstract as final step for all jurisdictions
    steps.append(("abstract", abstract))

    return steps


def execute_analysis_step(state, name, func):
    """
    Execute a single analysis step.
    
    Args:
        state: The current analysis state
        name: Name of the analysis step
        func: Function to execute for this step
        
    Returns:
        bool: True if step was executed, False if already completed
    """
    if not state.get(f"{name}_printed"):
        result = func(state)
        state.update(result)

        # Get proper display name for the step
        display_name = get_step_display_name(name, state)

        # Display analysis step label
        st.markdown(f"**{display_name}**")

        # Special handling for PIL provisions
        if name == "pil_provisions":
            formatted_content = display_pil_provisions(state, name)
            if formatted_content:
                st.markdown(f"<div class='machine-message'>{formatted_content}</div>", unsafe_allow_html=True)
                # Store formatted content for chat history
                state.setdefault("chat_history", []).append(("machine", f"{display_name}: {formatted_content}"))
            else:
                # Fallback to original format
                out = state.get(name)
                last = out[-1] if isinstance(out, list) else out
                st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
                state.setdefault("chat_history", []).append(("machine", f"{display_name}: {last}"))
        else:
            # Standard handling for other steps
            out = state.get(name)
            last = out[-1] if isinstance(out, list) else out
            st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
            state.setdefault("chat_history", []).append(("machine", f"{display_name}: {last}"))

        state[f"{name}_printed"] = True
        st.rerun()
        return True
    return False


def handle_step_scoring(state, name):
    """
    Handle scoring for an analysis step.
    
    Args:
        state: The current analysis state
        name: Name of the analysis step
        
    Returns:
        bool: True if scoring is complete
    """
    score_key = f"{name}_score_submitted"
    display_name = get_step_display_name(name, state)

    if not state.get(score_key):
        # Score input restricted to 0–100
        score = st.slider(
            f"Evaluate this {display_name} (0-100):",
            min_value=0,
            max_value=100,
            value=100,
            step=1,
            key=f"{name}_score_input"
        )
        if st.button(f"Submit {display_name} Score", key=f"submit_{name}_score"):
            # Record user score and add to history
            state[f"{name}_score"] = score
            state[score_key] = True
            state.setdefault("chat_history", []).append(("user", f"Score for {display_name}: {score}"))
            st.rerun()
        return False
    return True


def handle_step_editing(state, name, steps):
    """
    Handle editing for an analysis step.
    
    Args:
        state: The current analysis state
        name: Name of the analysis step
        steps: List of all analysis steps
    """
    display_name = get_step_display_name(name, state)

    # Special handling for PIL provisions
    if name == "pil_provisions":
        formatted_content = display_pil_provisions(state, name)
        if formatted_content:
            edited = handle_pil_provisions_editing(state, name, display_name, formatted_content)
        else:
            # Fallback to standard editing
            content = state.get(name)
            last = content[-1] if isinstance(content, list) else content
            edit_key = f"{name}_edited"
            edited = st.text_area(
                f"Edit {display_name}:",
                value=state.get(edit_key, last),
                height=200,
                key=f"{name}_edit_area"
            )
    else:
        # Standard editing for other steps
        content = state.get(name)
        last = content[-1] if isinstance(content, list) else content
        edit_key = f"{name}_edited"
        edited = st.text_area(
            f"Edit {display_name}:",
            value=state.get(edit_key, last),
            height=200,
            key=f"{name}_edit_area"
        )

    if st.button(f"Submit Edited {display_name}", key=f"submit_edited_{name}"):
        # Special handling for PIL provisions storage
        if name == "pil_provisions":
            update_pil_provisions_state(state, name, edited)
        else:
            # Standard handling for other steps
            state[name][-1] = edited
            state[f"{name}_edited"] = edited

        # Add to chat history
        state.setdefault("chat_history", []).append(("user", edited))

        # Advance to next step or complete analysis
        if state["analysis_step"] < len(steps) - 1:
            state["analysis_step"] += 1
        else:
            state["analysis_done"] = True

        print_state("\n\n\nUpdated CoLD State after analysis step\n\n", state)
        st.rerun()


def process_current_analysis_step(state):
    """
    Process the current analysis step.
    
    Args:
        state: The current analysis state
    """
    steps = get_analysis_steps(state)
    name, func = steps[state["analysis_step"]]

    # Execute the step if not already done
    execute_analysis_step(state, name, func)

    # Handle scoring
    scoring_complete = handle_step_scoring(state, name)

    # Handle editing after scoring
    if scoring_complete:
        handle_step_editing(state, name, steps)


def render_analysis_workflow(state):
    """
    Render the complete analysis workflow.
    
    Args:
        state: The current analysis state
    """
    if not state.get("analysis_ready"):
        return

    # Display analysis history
    display_analysis_history(state)

    # Check if analysis is complete
    if display_completion_message(state):
        return

    # Process current analysis step
    process_current_analysis_step(state)
