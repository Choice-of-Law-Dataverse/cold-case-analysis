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
    CaseCitationOutput,
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
from utils.state_manager import reset_workflow_state

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

        if isinstance(result, CaseCitationOutput):
            state["case_citation"] = result.case_citation
            state.setdefault("case_citation_confidence", []).append(result.confidence)
            state.setdefault("case_citation_reasoning", []).append(result.reasoning)
            return "case_citation"

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


def render_email_input():
    """Render optional email input for contact consent."""
    st.markdown("**Contact Email (optional):**")
    st.caption("If you agree to be contacted about your contributed cases and analyses, provide an email address.")
    return st.text_input(
        label="Email",
        key="user_email",
        placeholder="name@example.com",
        label_visibility="collapsed",
    )


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
        "col_section": "Choice of Law Sections",
        "case_citation": "Case Citation",
        "themes": "Themes",
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


def render_results_as_markdown(state):
    """
    Render all analysis results as markdown (read-only view mode).

    Args:
        state: The current analysis state
    """
    from components.confidence_display import add_confidence_chip_css, render_confidence_chip

    add_confidence_chip_css()
    steps = get_analysis_steps(state)

    st.header("Analysis Results")

    # Case Citation
    case_citation = state.get("case_citation", "N/A")
    if case_citation:
        confidence_key = "case_citation_confidence"
        reasoning_key = "case_citation_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Case Citation")
            if confidence:
                render_confidence_chip(confidence, reasoning, "view_case_citation")

        st.markdown(case_citation)
        st.markdown("---")

    # Themes
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
                render_confidence_chip(confidence, reasoning, "view_themes")

        st.markdown(f"**{current_themes}**")
        st.markdown("---")

    # Choice of Law Section
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
                render_confidence_chip(confidence, reasoning, "view_col_section")

        st.markdown(current_col)
        st.markdown("---")

    # Analysis Steps
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
                render_confidence_chip(confidence, reasoning, f"view_{name}")

        if name == "pil_provisions":
            # Display PIL provisions as formatted list
            if isinstance(current_value, list):
                for provision in current_value:
                    st.markdown(f"- {provision}")
            else:
                st.markdown(current_value)
        else:
            st.markdown(current_value)

        st.markdown("---")


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


def execute_all_analysis_steps_with_generator(state):
    """
    Execute all analysis steps using the generator pattern.
    The workflow logic is in the tool, this just handles UI updates.

    Args:
        state: The current analysis state
    """
    text = state["full_text"]
    legal_system = state.get("jurisdiction", "Civil-law jurisdiction")
    jurisdiction = state.get("precise_jurisdiction")
    model = state.get("model") or os.getenv("OPENAI_MODEL") or "gpt-5-nano"

    # Create progress placeholder
    progress_placeholder = st.empty()
    progress_placeholder.progress(0, text="Analysis in progress... it can take a few minutes.")

    # Create results container
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
        ):
            # Update state using helper class
            step_name = WorkflowStateUpdater.update_state(state, result)

            # Mark step as printed
            state[f"{step_name}_printed"] = True

            # Update progress
            completed += 1
            progress = completed / total_steps
            progress_placeholder.progress(min(progress, 1.0), text=f"Completed {completed}/{total_steps} steps")

            # Display result in results container
            with results_container:
                st.markdown(f"✅ {get_step_display_name(step_name, state)}")

        # Clear progress when done
        progress_placeholder.empty()
    except Exception as e:
        progress_placeholder.empty()
        st.error(f"Error during analysis: {str(e)}")
        logger.error(f"Analysis workflow error: {e}", exc_info=True)
        raise


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
        min-height: 100px !important;
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

    st.header("Review and Edit Results")

    # Section 0: Case Citation

    case_citation = state.get("case_citation", "N/A")
    if case_citation:
        confidence_key = "case_citation_confidence"
        reasoning_key = "case_citation_reasoning"
        confidence_list = state.get(confidence_key, [])
        reasoning_list = state.get(reasoning_key, [])
        confidence = confidence_list[-1] if confidence_list else None
        reasoning = reasoning_list[-1] if reasoning_list else "No reasoning available"

        with st.container(horizontal=True):
            st.subheader("Case Citation")
            if confidence:
                render_confidence_chip(confidence, reasoning, "final_edit_case_citation")

        edited_case_citation = st.text_area(
            "Edit Case Citation",
            value=case_citation,
            key="final_edit_case_citation_text",
            height=100,
            label_visibility="collapsed",
        )
        edited_values["case_citation"] = edited_case_citation

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
            "Edit Choice of Law Section",
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
                f"{display_name}", value=str(current_value), key=f"final_edit_{name}", label_visibility="collapsed", height=300
            )
            edited_values[name] = edited

    render_email_input()

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

            # Handle the case where state[name] might be a string or list
            if name == "pil_provisions":
                try:
                    parsed = json.loads(edited_value)
                    if isinstance(state[name], list):
                        state[name][-1] = parsed
                    else:
                        state[name] = [parsed]
                    state[f"{name}_edited"] = parsed
                except json.JSONDecodeError:
                    if isinstance(state[name], list):
                        state[name][-1] = edited_value
                    else:
                        state[name] = [edited_value]
                    state[f"{name}_edited"] = edited_value
            else:
                if isinstance(state[name], list):
                    state[name][-1] = edited_value
                else:
                    state[name] = [edited_value]
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
        # Analysis is done - show completion message, results in view mode, and action buttons
        display_completion_message(state)

        # Render results as markdown (read-only)
        render_results_as_markdown(state)

        # Add action buttons in a horizontal layout
        col1, col2, _ = st.columns([1, 1, 3])

        with col1:
            if st.button("🖨️ Print", key="print_button", help="Print the analysis results"):
                # Inject JavaScript to trigger browser print dialog
                st.markdown(
                    """
                    <script>
                    window.print();
                    </script>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            if st.button("📝 New Submission", key="new_submission_button", help="Start a new case analysis"):
                reset_workflow_state()
                st.rerun()

