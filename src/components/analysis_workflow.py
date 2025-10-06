# components/analysis_workflow.py
"""
Analysis workflow components for the CoLD Case Analyzer.
"""

import json
import logging

import streamlit as st

from components.database import save_to_db
from components.pil_provisions_handler import display_pil_provisions
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
        # Extract parameters from state
        import os
        text = state["full_text"]
        col_section = state.get("col_section", [""])[-1] if state.get("col_section") else ""
        jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
        specific_jurisdiction = state.get("precise_jurisdiction")
        model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"
        
        # Call function with explicit parameters
        if name == "relevant_facts":
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model)
            state.setdefault("relevant_facts", []).append(result.relevant_facts)
            state.setdefault("relevant_facts_confidence", []).append(result.confidence)
            state.setdefault("relevant_facts_reasoning", []).append(result.reasoning)
        elif name == "pil_provisions":
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model)
            state.setdefault("pil_provisions", []).append(result.pil_provisions)
            state.setdefault("pil_provisions_confidence", []).append(result.confidence)
            state.setdefault("pil_provisions_reasoning", []).append(result.reasoning)
        elif name == "col_issue":
            # Get classification themes
            classification_messages = state.get("classification", [])
            themes_list: list[str] = []
            if classification_messages:
                last_msg = classification_messages[-1]
                if hasattr(last_msg, "content"):
                    content_value = last_msg.content
                    if isinstance(content_value, list):
                        themes_list = content_value
                    elif isinstance(content_value, str) and content_value:
                        themes_list = [t.strip() for t in last_msg.split(",")]
                elif isinstance(last_msg, str):
                    themes_list = [t.strip() for t in last_msg.split(",")]
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model, themes_list)
            state.setdefault("col_issue", []).append(result.col_issue)
            state.setdefault("col_issue_confidence", []).append(result.confidence)
            state.setdefault("col_issue_reasoning", []).append(result.reasoning)
        elif name == "courts_position":
            classification = state.get("classification", [""])[-1] if state.get("classification") else ""
            col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue)
            state.setdefault("courts_position", []).append(result.courts_position)
            state.setdefault("courts_position_confidence", []).append(result.confidence)
            state.setdefault("courts_position_reasoning", []).append(result.reasoning)
        elif name == "obiter_dicta":
            classification = state.get("classification", [""])[-1] if state.get("classification") else ""
            col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue)
            state.setdefault("obiter_dicta", []).append(result.obiter_dicta)
            state.setdefault("obiter_dicta_confidence", []).append(result.confidence)
            state.setdefault("obiter_dicta_reasoning", []).append(result.reasoning)
        elif name == "dissenting_opinions":
            classification = state.get("classification", [""])[-1] if state.get("classification") else ""
            col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
            result = func(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue)
            state.setdefault("dissenting_opinions", []).append(result.dissenting_opinions)
            state.setdefault("dissenting_opinions_confidence", []).append(result.confidence)
            state.setdefault("dissenting_opinions_reasoning", []).append(result.reasoning)
        elif name == "abstract":
            classification = state.get("classification", [""])[-1] if state.get("classification") else ""
            facts = state.get("relevant_facts", [""])[-1] if state.get("relevant_facts") else ""
            pil_provisions = state.get("pil_provisions", [""])[-1] if state.get("pil_provisions") else ""
            col_issue = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""
            court_position = state.get("courts_position", [""])[-1] if state.get("courts_position") else ""
            obiter_dicta = state.get("obiter_dicta", [""])[-1] if state.get("obiter_dicta") else ""
            dissenting_opinions = state.get("dissenting_opinions", [""])[-1] if state.get("dissenting_opinions") else ""
            result = func(text, jurisdiction, specific_jurisdiction, model, classification, facts, pil_provisions, col_issue, court_position, obiter_dicta, dissenting_opinions)
            state.setdefault("abstract", []).append(result.abstract)
            state.setdefault("abstract_confidence", []).append(result.confidence)
            state.setdefault("abstract_reasoning", []).append(result.reasoning)

        display_name = get_step_display_name(name, state)

        st.markdown(f"**{display_name}**")

        if name == "pil_provisions":
            formatted_content = display_pil_provisions(state, name)
            if formatted_content:
                st.markdown(f"<div class='machine-message'>{formatted_content}</div>", unsafe_allow_html=True)
                state.setdefault("chat_history", []).append(("machine", f"{display_name}: {formatted_content}"))
            else:
                out = state.get(name)
                last = out[-1] if isinstance(out, list) else out
                st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
                state.setdefault("chat_history", []).append(("machine", f"{display_name}: {last}"))
        else:
            out = state.get(name)
            last = out[-1] if isinstance(out, list) else out
            st.markdown(f"<div class='machine-message'>{last}</div>", unsafe_allow_html=True)
            state.setdefault("chat_history", []).append(("machine", f"{display_name}: {last}"))

        state[f"{name}_printed"] = True
        st.rerun()
        return True
    return False


def handle_step_editing(state, name, steps):
    """
    Store edited content without showing editing UI during processing.

    Args:
        state: The current analysis state
        name: Name of the analysis step
        steps: List of all analysis steps
    """
    # Automatically advance to next step without editing during processing
    if state["analysis_step"] < len(steps) - 1:
        state["analysis_step"] += 1
    else:
        state["analysis_done"] = True

    print_state("\n\n\nUpdated CoLD State after analysis step\n\n", state)
    st.rerun()


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

    # Extract common parameters from state
    import os
    text = state["full_text"]
    col_section = state.get("col_section", [""])[-1] if state.get("col_section") else ""
    jurisdiction = state.get("jurisdiction", "Civil-law jurisdiction")
    specific_jurisdiction = state.get("precise_jurisdiction")
    model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    # Steps that can run in parallel (don't depend on each other)
    parallel_steps = [
        ("relevant_facts", lambda: relevant_facts(text, col_section, jurisdiction, specific_jurisdiction, model)),
        ("pil_provisions", lambda: pil_provisions(text, col_section, jurisdiction, specific_jurisdiction, model)),
    ]

    st.markdown("**Analyzing case...**")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Execute parallel steps
    completed = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(func): name for name, func in parallel_steps}
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                # Update state with results
                if name == "relevant_facts":
                    state.setdefault("relevant_facts", []).append(result.relevant_facts)
                    state.setdefault("relevant_facts_confidence", []).append(result.confidence)
                    state.setdefault("relevant_facts_reasoning", []).append(result.reasoning)
                elif name == "pil_provisions":
                    state.setdefault("pil_provisions", []).append(result.pil_provisions)
                    state.setdefault("pil_provisions_confidence", []).append(result.confidence)
                    state.setdefault("pil_provisions_reasoning", []).append(result.reasoning)
                
                completed += 1
                total_steps = 2 + (1 if state.get("jurisdiction") != "Common-law jurisdiction" else 3) + 2
                progress = completed / total_steps
                progress_bar.progress(progress)
                status_text.text(f"Completed: {get_step_display_name(name, state)}")
            except Exception as e:
                st.error(f"Error processing {name}: {str(e)}")

    # Get classification themes for col_issue
    classification_messages = state.get("classification", [])
    themes_list: list[str] = []
    if classification_messages:
        last_msg = classification_messages[-1]
        if hasattr(last_msg, "content"):
            content_value = last_msg.content
            if isinstance(content_value, list):
                themes_list = content_value
            elif isinstance(content_value, str) and content_value:
                themes_list = [t.strip() for t in last_msg.split(",")]
        elif isinstance(last_msg, str):
            themes_list = [t.strip() for t in last_msg.split(",")]

    # Execute col_issue (depends on classification)
    try:
        result = col_issue(text, col_section, jurisdiction, specific_jurisdiction, model, themes_list)
        state.setdefault("col_issue", []).append(result.col_issue)
        state.setdefault("col_issue_confidence", []).append(result.confidence)
        state.setdefault("col_issue_reasoning", []).append(result.reasoning)
        completed += 1
        progress = completed / (2 + (1 if state.get("jurisdiction") != "Common-law jurisdiction" else 3) + 2)
        progress_bar.progress(progress)
        status_text.text(f"Completed: {get_step_display_name('col_issue', state)}")
    except Exception as e:
        st.error(f"Error processing col_issue: {str(e)}")

    # Execute sequential steps that depend on col_issue
    classification = state.get("classification", [""])[-1] if state.get("classification") else ""
    col_issue_text = state.get("col_issue", [""])[-1] if state.get("col_issue") else ""

    sequential_steps = [
        ("courts_position", lambda: courts_position(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue_text)),
    ]

    if state.get("jurisdiction") == "Common-law jurisdiction":
        sequential_steps.extend([
            ("obiter_dicta", lambda: obiter_dicta(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue_text)),
            ("dissenting_opinions", lambda: dissenting_opinions(text, col_section, jurisdiction, specific_jurisdiction, model, classification, col_issue_text)),
        ])

    for name, func in sequential_steps:
        try:
            result = func()
            # Update state with results
            if name == "courts_position":
                state.setdefault("courts_position", []).append(result.courts_position)
                state.setdefault("courts_position_confidence", []).append(result.confidence)
                state.setdefault("courts_position_reasoning", []).append(result.reasoning)
            elif name == "obiter_dicta":
                state.setdefault("obiter_dicta", []).append(result.obiter_dicta)
                state.setdefault("obiter_dicta_confidence", []).append(result.confidence)
                state.setdefault("obiter_dicta_reasoning", []).append(result.reasoning)
            elif name == "dissenting_opinions":
                state.setdefault("dissenting_opinions", []).append(result.dissenting_opinions)
                state.setdefault("dissenting_opinions_confidence", []).append(result.confidence)
                state.setdefault("dissenting_opinions_reasoning", []).append(result.reasoning)
            
            completed += 1
            total_steps = 2 + (1 if state.get("jurisdiction") != "Common-law jurisdiction" else 3) + 2
            progress = completed / total_steps
            progress_bar.progress(progress)
            status_text.text(f"Completed: {get_step_display_name(name, state)}")
        except Exception as e:
            st.error(f"Error processing {name}: {str(e)}")

    # Finally, execute abstract
    try:
        facts = state.get("relevant_facts", [""])[-1] if state.get("relevant_facts") else ""
        pil_provisions_data = state.get("pil_provisions", [""])[-1] if state.get("pil_provisions") else ""
        court_position = state.get("courts_position", [""])[-1] if state.get("courts_position") else ""
        obiter_dicta_text = state.get("obiter_dicta", [""])[-1] if state.get("obiter_dicta") else ""
        dissenting_opinions_text = state.get("dissenting_opinions", [""])[-1] if state.get("dissenting_opinions") else ""
        
        result = abstract(text, jurisdiction, specific_jurisdiction, model, classification, facts, pil_provisions_data, col_issue_text, court_position, obiter_dicta_text, dissenting_opinions_text)
        state.setdefault("abstract", []).append(result.abstract)
        state.setdefault("abstract_confidence", []).append(result.confidence)
        state.setdefault("abstract_reasoning", []).append(result.reasoning)
        
        completed += 1
        progress_bar.progress(1.0)
        status_text.text(f"Completed: {get_step_display_name('abstract', state)}")
    except Exception as e:
        st.error(f"Error processing abstract: {str(e)}")

    progress_bar.progress(1.0)
    status_text.text("✓ Analysis complete!")

    # Mark all steps as printed
    for name, _ in parallel_steps:
        state[f"{name}_printed"] = True
    state["col_issue_printed"] = True
    for name, _ in sequential_steps:
        state[f"{name}_printed"] = True
    state["abstract_printed"] = True


def render_final_editing_phase(state):
    """
    Render the final editing phase where all results are shown as editable text areas.

    Args:
        state: The current analysis state
    """
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip

    add_confidence_chip_css()

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

        confidence_key = f"{name}_confidence"
        reasoning_key = f"{name}_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader(display_name)
            if confidence:
                render_confidence_chip(confidence, reasoning, f"analysis_{name}")

        if name == "pil_provisions":
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

            edited = st.text_area(
                f"Edit {display_name} (JSON format):", value=edit_value, key=f"final_edit_{name}", label_visibility="collapsed"
            )
            edited_values[name] = edited
        else:
            edited = st.text_area(
                f"{display_name}", value=str(current_value), key=f"final_edit_{name}", label_visibility="collapsed"
            )
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
        execute_all_analysis_steps_parallel(state)
        state["parallel_execution_started"] = True
        st.rerun()
    elif not state.get("analysis_done"):
        render_final_editing_phase(state)
    else:
        display_completion_message(state)
