"""
Analysis workflow components for the CoLD Case Analyzer.
"""

import json
import logging

import streamlit as st

from components.database import save_to_db
from utils.debug_print_state import print_state

logger = logging.getLogger(__name__)


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
        "abstract": "Abstract",
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
            if ": " in msg:
                step_label, content = msg.split(": ", 1)

                st.markdown(f"**{step_label}**")

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
        logger.info("Analysis completed, saving state to database")
        save_to_db(state)
        st.markdown(
            "<div class='machine-message'>Thank you for using the CoLD Case Analyzer.<br>"
            "If you would like to find out more about the project, please visit "
            '<a href="https://cold.global" target="_blank">cold.global</a></div>',
            unsafe_allow_html=True,
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

    steps = [
        ("relevant_facts", relevant_facts),
        ("pil_provisions", pil_provisions),
        ("col_issue", col_issue),
        ("courts_position", courts_position),
    ]

    if state.get("jurisdiction") == "Common-law jurisdiction":
        steps.extend([("obiter_dicta", obiter_dicta), ("dissenting_opinions", dissenting_opinions)])

    steps.append(("abstract", abstract))

    return steps


def execute_all_analysis_steps_parallel(state):
    """
    Execute all analysis steps in parallel where possible.
    This runs all steps without user interaction and stores results.

    Args:
        state: The current analysis state
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from tools.case_analyzer import (
        abstract,
        col_issue,
        courts_position,
        dissenting_opinions,
        obiter_dicta,
        pil_provisions,
        relevant_facts,
    )

    parallel_steps = [
        ("relevant_facts", relevant_facts),
        ("pil_provisions", pil_provisions),
        ("col_issue", col_issue),
    ]

    sequential_steps = [("courts_position", courts_position)]

    if state.get("jurisdiction") == "Common-law jurisdiction":
        sequential_steps.extend([("obiter_dicta", obiter_dicta), ("dissenting_opinions", dissenting_opinions)])

    sequential_steps.append(("abstract", abstract))

    from utils.progress_banner import hide_progress_banner, show_progress_banner

    total_steps = len(parallel_steps) + len(sequential_steps)
    completed = 0

    def update_banner(message, progress):
        """Update the progress banner with current status."""
        show_progress_banner(message, progress)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(func, state): name for name, func in parallel_steps}

        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                state.update(result)
                completed += 1
                progress = completed / total_steps
                update_banner(f"Analyzing case... Completed: {get_step_display_name(name, state)}", progress)
            except Exception as e:
                st.error(f"Error processing {name}: {str(e)}")

    for name, func in sequential_steps:
        try:
            result = func(state)
            state.update(result)
            completed += 1
            progress = completed / total_steps
            update_banner(f"Analyzing case... Completed: {get_step_display_name(name, state)}", progress)
        except Exception as e:
            st.error(f"Error processing {name}: {str(e)}")

    update_banner("✓ Analysis complete!", 1.0)

    import time

    time.sleep(1)

    hide_progress_banner()

    for name, _ in parallel_steps + sequential_steps:
        state[f"{name}_printed"] = True
        state[f"{name}_score_submitted"] = True


def render_final_editing_phase(state):
    """
    Render the final editing phase where all results are shown as editable text areas.

    Args:
        state: The current analysis state
    """
    st.markdown("---")
    st.markdown("## Review and Edit Analysis Results")
    st.markdown("Review all analysis results below. You can edit any section before final submission.")

    steps = get_analysis_steps(state)
    edited_values = {}

    st.markdown(
        """
    <style>
    /* Default height for all textareas */
    div[data-testid="stTextArea"] textarea {
        min-height: 400px !important;
        max-height: 66vh !important;
        resize: vertical !important;
    }

    /* Shorter textarea for COL Issue step */
    div[data-testid="stTextArea"]:has(textarea[aria-label*="final_edit_col_issue"]) textarea {
        min-height: 200px !important;
        max-height: 30vh !important;
    }

    /* Medium height for PIL provisions JSON editing */
    div[data-testid="stTextArea"]:has(textarea[aria-label*="final_edit_pil_provisions"]) textarea {
        min-height: 300px !important;
        max-height: 50vh !important;
    }

    /* Fallback selectors for broader browser support */
    textarea[aria-label*="Choice of Law Issue"] {
        min-height: 200px !important;
        max-height: 30vh !important;
    }

    textarea[aria-label*="JSON format"] {
        min-height: 300px !important;
        max-height: 50vh !important;
    }

    /* Chip styling for PIL provisions */
    .pil-chip {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        border: 1px solid #1976d2;
        border-radius: 16px;
        padding: 6px 12px;
        margin: 4px;
        font-size: 14px;
    }
    .pil-chips-container {
        margin: 10px 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    for name, _ in steps:
        display_name = get_step_display_name(name, state)

        content = state.get(name)
        if not content:
            continue

        current_value = content[-1] if isinstance(content, list) else content

        if name == "pil_provisions":
            st.markdown(f"**{display_name}**")

            if isinstance(current_value, list):
                chips_html = '<div class="pil-chips-container">'
                for provision in current_value:
                    provision_str = str(provision).strip('"')
                    chips_html += f'<span class="pil-chip">{provision_str}</span>'
                chips_html += "</div>"
                st.markdown(chips_html, unsafe_allow_html=True)

                edit_value = json.dumps(current_value, indent=2)
            else:
                edit_value = str(current_value)

            edited = st.text_area(f"Edit {display_name} (JSON format):", value=edit_value, key=f"final_edit_{name}")
            edited_values[name] = edited
        else:
            edited = st.text_area(f"**{display_name}**", value=str(current_value), key=f"final_edit_{name}")
            edited_values[name] = edited

    if st.button("Submit Final Analysis", type="primary", key="submit_final_analysis"):
        for name, edited_value in edited_values.items():
            if name == "pil_provisions":
                try:
                    parsed = json.loads(edited_value)
                    state[name][-1] = parsed
                    state[f"{name}_edited"] = parsed
                except json.JSONDecodeError:
                    state[name][-1] = edited_value
                    state[f"{name}_edited"] = edited_value
            else:
                state[name][-1] = edited_value
                state[f"{name}_edited"] = edited_value

        state["analysis_done"] = True
        print_state("\n\n\nFinal CoLD State after editing\n\n", state)
        st.rerun()


def render_analysis_workflow(state):
    """
    Render the complete analysis workflow with parallel execution and final editing.

    Args:
        state: The current analysis state
    """
    if not state.get("analysis_ready"):
        return

    if not state.get("parallel_execution_started"):
        state["parallel_execution_started"] = True
        execute_all_analysis_steps_parallel(state)

        st.rerun()
    elif state.get("analysis_done"):
        display_completion_message(state)
    else:
        render_final_editing_phase(state)
