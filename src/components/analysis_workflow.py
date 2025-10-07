# components/analysis_workflow.py
"""
Analysis workflow components for the CoLD Case Analyzer.
"""

import json
import logging
import os

import streamlit as st

from components.database import save_to_db
from models.analysis_models import (
    AbstractOutput,
    ColIssueOutput,
    ColSectionOutput,
    CourtsPositionOutput,
    DissentingOpinionsOutput,
    ObiterDictaOutput,
    PILProvisionsOutput,
    RelevantFactsOutput,
)
from models.classification_models import ThemeClassificationOutput
from tools.case_analyzer import analyze_case_workflow
from utils.debug_print_state import print_state

logger = logging.getLogger(__name__)


class WorkflowStateUpdater:
    """Helper class to update state based on output type."""

    @staticmethod
    def update_state(state: dict, result: object) -> str:
        """
        Update state based on the result type.

        Args:
            state: The current analysis state dictionary
            result: The output object from analysis

        Returns:
            str: The step name for this result type
        """
        if isinstance(result, ColSectionOutput):
            # Join multiple sections with newlines
            col_section_text = "\n\n".join(result.col_sections) if result.col_sections else ""
            state.setdefault("col_section", []).append(col_section_text)
            state.setdefault("col_section_confidence", []).append(result.confidence)
            state.setdefault("col_section_reasoning", []).append(result.reasoning)
            return "col_section"

        elif isinstance(result, ThemeClassificationOutput):
            themes_str = ", ".join(result.themes) if isinstance(result.themes, list) else str(result.themes)
            state.setdefault("classification", []).append(themes_str)
            state.setdefault("classification_confidence", []).append(result.confidence)
            state.setdefault("classification_reasoning", []).append(result.reasoning)
            return "themes"

        elif isinstance(result, RelevantFactsOutput):
            state.setdefault("relevant_facts", []).append(result.relevant_facts)
            state.setdefault("relevant_facts_confidence", []).append(result.confidence)
            state.setdefault("relevant_facts_reasoning", []).append(result.reasoning)
            return "relevant_facts"

        elif isinstance(result, PILProvisionsOutput):
            state.setdefault("pil_provisions", []).append(result.pil_provisions)
            state.setdefault("pil_provisions_confidence", []).append(result.confidence)
            state.setdefault("pil_provisions_reasoning", []).append(result.reasoning)
            return "pil_provisions"

        elif isinstance(result, ColIssueOutput):
            state.setdefault("col_issue", []).append(result.col_issue)
            state.setdefault("col_issue_confidence", []).append(result.confidence)
            state.setdefault("col_issue_reasoning", []).append(result.reasoning)
            return "col_issue"

        elif isinstance(result, CourtsPositionOutput):
            state.setdefault("courts_position", []).append(result.courts_position)
            state.setdefault("courts_position_confidence", []).append(result.confidence)
            state.setdefault("courts_position_reasoning", []).append(result.reasoning)
            return "courts_position"

        elif isinstance(result, ObiterDictaOutput):
            state.setdefault("obiter_dicta", []).append(result.obiter_dicta)
            state.setdefault("obiter_dicta_confidence", []).append(result.confidence)
            state.setdefault("obiter_dicta_reasoning", []).append(result.reasoning)
            return "obiter_dicta"

        elif isinstance(result, DissentingOpinionsOutput):
            state.setdefault("dissenting_opinions", []).append(result.dissenting_opinions)
            state.setdefault("dissenting_opinions_confidence", []).append(result.confidence)
            state.setdefault("dissenting_opinions_reasoning", []).append(result.reasoning)
            return "dissenting_opinions"

        elif isinstance(result, AbstractOutput):
            state.setdefault("abstract", []).append(result.abstract)
            state.setdefault("abstract_confidence", []).append(result.confidence)
            state.setdefault("abstract_reasoning", []).append(result.reasoning)
            return "abstract"

        else:
            raise ValueError(f"Unknown result type: {type(result)}")


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
        list: List of (name, None) tuples for analysis steps (functions not needed with generator)
    """
    steps = [
        ("relevant_facts", None),
        ("pil_provisions", None),
        ("col_issue", None),
        ("courts_position", None),
    ]

    if state.get("jurisdiction") == "Common-law jurisdiction":
        steps.extend([("obiter_dicta", None), ("dissenting_opinions", None)])

    steps.append(("abstract", None))

    return steps


def render_partial_step(step_name: str, state: dict):
    """
    Render a single analysis step in read-only mode during generation.

    Args:
        step_name: Name of the step to render
        state: The current analysis state
    """
    from components.confidence_display import render_confidence_chip
    from utils.data_loaders import load_valid_themes

    # Handle themes specially
    if step_name == "themes":
        classification = state.get("classification", [])
        if not classification:
            return

        current_themes = classification[-1] if isinstance(classification, list) else classification
        confidence_key = "classification_confidence"
        reasoning_key = "classification_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Themes")
            if confidence:
                render_confidence_chip(confidence, reasoning, f"partial_{step_name}")

        valid_themes = load_valid_themes()
        valid_themes.append("NA")
        default_sel = [t.strip() for t in current_themes.split(",") if t.strip()] if isinstance(current_themes, str) else []
        theme_mapping = {theme.lower(): theme for theme in valid_themes}
        filtered_defaults = []
        for theme in default_sel:
            if theme in valid_themes:
                filtered_defaults.append(theme)
            elif theme.lower() in theme_mapping:
                filtered_defaults.append(theme_mapping[theme.lower()])

        st.multiselect(
            "Themes (read-only):",
            options=valid_themes,
            default=filtered_defaults,
            key=f"partial_{step_name}",
            label_visibility="collapsed",
            disabled=True,
        )
        return

    # Handle col_section specially
    if step_name == "col_section":
        col_section = state.get("col_section", [])
        if not col_section:
            return

        current_col = col_section[-1] if isinstance(col_section, list) else col_section
        confidence_key = "col_section_confidence"
        reasoning_key = "col_section_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Choice of Law Section")
            if confidence:
                render_confidence_chip(confidence, reasoning, f"partial_{step_name}")

        st.text_area(
            "Choice of Law Section (read-only):",
            value=str(current_col),
            key=f"partial_{step_name}",
            height=300,
            label_visibility="collapsed",
            disabled=True,
        )
        return

    # Handle regular analysis steps
    display_name = get_step_display_name(step_name, state)
    content = state.get(step_name)

    if not content:
        return

    current_value = content[-1] if isinstance(content, list) else content

    confidence_key = f"{step_name}_confidence"
    reasoning_key = f"{step_name}_reasoning"
    confidence_list = state.get(confidence_key, [])
    reasoning_list = state.get(reasoning_key, [])
    confidence = confidence_list[-1] if confidence_list else None
    reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

    with st.container(horizontal=True):
        st.subheader(display_name)
        if confidence:
            render_confidence_chip(confidence, reasoning, f"partial_{step_name}")

    if step_name == "pil_provisions":
        if isinstance(current_value, list):
            chips_html = '<div class="pil-chips-container">'
            for provision in current_value:
                provision_str = str(provision).strip('"')
                chips_html += f'<span class="pil-chip">{provision_str}</span>'
            chips_html += "</div>"
            st.markdown(chips_html, unsafe_allow_html=True)

            display_value = json.dumps(current_value, indent=2)
        else:
            display_value = str(current_value)

        st.text_area(
            f"{display_name} (read-only)",
            value=display_value,
            key=f"partial_{step_name}",
            label_visibility="collapsed",
            disabled=True,
            height=300,
        )
    else:
        st.text_area(
            f"{display_name} (read-only)",
            value=str(current_value),
            key=f"partial_{step_name}",
            label_visibility="collapsed",
            disabled=True,
            height=400,
        )


def execute_all_analysis_steps_with_generator(state):
    """
    Execute all analysis steps using the generator pattern.
    The workflow logic is in the tool, this just handles UI updates.

    Args:
        state: The current analysis state
    """
    from components.confidence_display import add_confidence_chip_css

    text = state["full_text"]
    col_sections = None
    col_section_data = state.get("col_section", [])
    if col_section_data:
        col_section_text = col_section_data[-1] if isinstance(col_section_data, list) else col_section_data
        # Convert back to list for generator
        col_sections = [col_section_text] if col_section_text else None

    legal_system = state.get("jurisdiction", "Civil-law jurisdiction")
    jurisdiction = state.get("precise_jurisdiction")
    model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    # Get themes if already classified
    classification_messages = state.get("classification", [])
    themes = None
    if classification_messages:
        last_msg = classification_messages[-1]
        if hasattr(last_msg, "content"):
            content_value = last_msg.content
            if isinstance(content_value, list):
                themes = content_value
            elif isinstance(content_value, str) and content_value:
                themes = [t.strip() for t in content_value.split(",")]
        elif isinstance(last_msg, str):
            themes = [t.strip() for t in last_msg.split(",")]

    st.markdown("**Analyzing case...**")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Add CSS for confidence chips and PIL provisions
    add_confidence_chip_css()
    st.markdown(
        """
    <style>
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

    # Create a container for partial results that will be updated as steps complete
    results_container = st.container()

    # Calculate total steps
    total_steps = 8  # col_section, themes, relevant_facts, pil_provisions, col_issue, courts_position, abstract
    if legal_system == "Common-law jurisdiction":
        total_steps += 2  # obiter_dicta, dissenting_opinions

    completed = 0

    try:
        # Use the generator to orchestrate the workflow
        for result in analyze_case_workflow(
            text=text,
            legal_system=legal_system,
            jurisdiction=jurisdiction,
            model=model,
            col_sections=col_sections,
            themes=themes,
        ):
            # Update state using helper class
            step_name = WorkflowStateUpdater.update_state(state, result)

            # Mark step as printed
            state[f"{step_name}_printed"] = True

            # Update progress
            completed += 1
            progress = completed / total_steps
            progress_bar.progress(min(progress, 1.0))
            status_text.text(f"Completed: {get_step_display_name(step_name, state)}")

            # Render partial result in the results container
            with results_container:
                render_partial_step(step_name, state)

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        logger.error(f"Analysis workflow error: {e}", exc_info=True)
        raise

    progress_bar.progress(1.0)
    status_text.text("✓ Analysis complete!")


def render_final_editing_phase():
    """
    Render the final editing phase where all results are shown as editable text areas.
    This includes themes, CoL section, and all analysis steps.
    """
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip
    from utils.data_loaders import load_valid_themes

    state = st.session_state.col_state
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

    st.markdown("## Review and Edit Results")
    st.markdown("Review all extracted information below. You can edit any field before final submission.")

    # Section 1: Themes

    classification = state.get("classification", [])
    if classification:
        current_themes = classification[-1] if isinstance(classification, list) else classification
        confidence_key = "classification_confidence"
        reasoning_key = "classification_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Themes")

            if confidence:
                render_confidence_chip(confidence, reasoning, "final_edit_themes")

        valid_themes = load_valid_themes()
        valid_themes.append("NA")

        default_sel = [t.strip() for t in current_themes.split(",") if t.strip()] if isinstance(current_themes, str) else []
        theme_mapping = {theme.lower(): theme for theme in valid_themes}
        filtered_defaults = []
        for theme in default_sel:
            if theme in valid_themes:
                filtered_defaults.append(theme)
            elif theme.lower() in theme_mapping:
                filtered_defaults.append(theme_mapping[theme.lower()])

        selected_themes = st.multiselect(
            "Select themes:",
            options=valid_themes,
            default=filtered_defaults,
            key="final_edit_themes_select",
            label_visibility="collapsed",
        )
        edited_values["themes"] = selected_themes

    # Section 2: Choice of Law Section

    col_section = state.get("col_section", [])
    if col_section:
        current_col = col_section[-1] if isinstance(col_section, list) else col_section
        confidence_key = "col_section_confidence"
        reasoning_key = "col_section_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Choice of Law Section")
            if confidence:
                render_confidence_chip(confidence, reasoning, "final_edit_col_section")

        edited_col = st.text_area(
            "Edit Choice of Law Section:",
            value=str(current_col),
            key="final_edit_col_section_text",
            height=300,
            label_visibility="collapsed",
        )
        edited_values["col_section"] = edited_col

    # Section 3: Analysis Steps
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
        # Update themes
        if "themes" in edited_values:
            new_themes = ", ".join(edited_values["themes"])
            state.setdefault("classification", []).append(new_themes)
            state["classification_edited"] = new_themes

        # Update CoL section
        if "col_section" in edited_values:
            state["col_section"][-1] = edited_values["col_section"]
            state["col_section_edited"] = edited_values["col_section"]

        # Update analysis steps
        for name, edited_value in edited_values.items():
            if name in ["themes", "col_section"]:
                continue
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


def render_analysis_workflow():
    """
    Render the complete analysis workflow with parallel execution and final editing.
    """
    state = st.session_state.col_state
    if not state.get("analysis_ready"):
        return

    if not state.get("parallel_execution_started"):
        execute_all_analysis_steps_with_generator(state)
        state["parallel_execution_started"] = True
        st.rerun()
    elif not state.get("analysis_done"):
        render_final_editing_phase()
    else:
        display_completion_message(state)
