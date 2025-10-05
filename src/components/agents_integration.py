"""Integration component for OpenAI Agents PoC with Streamlit."""

import asyncio
import logging

import streamlit as st

from openai_agents_poc.orchestrator import CaseAnalysisOrchestrator
from utils.data_loaders import load_valid_themes

logger = logging.getLogger(__name__)


def run_agents_workflow(
    case_text: str,
    case_citation: str,
    jurisdiction: str,
    precise_jurisdiction: str,
    model: str,
    username: str = None,
    user_email: str = None,
) -> dict:
    """
    Run the OpenAI Agents workflow and return results.

    Args:
        case_text: Full text of the court decision
        case_citation: Case citation
        jurisdiction: Legal system type (Civil-law/Common-law/Indian jurisdiction)
        precise_jurisdiction: Precise jurisdiction (e.g., Switzerland, USA)
        model: OpenAI model to use
        username: Optional username
        user_email: Optional user email

    Returns:
        dict: Analysis results in the format expected by the rest of the application
    """
    # Load valid themes
    valid_themes = load_valid_themes()

    # Initialize orchestrator
    orchestrator = CaseAnalysisOrchestrator(model=model, available_themes=valid_themes)

    # Create metadata
    case_metadata = {
        "username": username,
        "user_email": user_email,
        "jurisdiction": jurisdiction,
        "precise_jurisdiction": precise_jurisdiction,
    }

    # Run analysis
    try:
        result = asyncio.run(
            orchestrator.analyze_case(case_text=case_text, case_citation=case_citation, case_metadata=case_metadata)
        )

        # Convert to application state format
        return convert_agents_result_to_state(result)
    except Exception as e:
        logger.error(f"Error running agents workflow: {str(e)}")
        raise


def convert_agents_result_to_state(result) -> dict:
    """
    Convert OpenAI Agents result to application state format.

    Args:
        result: CompleteCaseAnalysis from agents workflow

    Returns:
        dict: State dictionary compatible with existing application
    """
    # Ensure col_sections is not empty, provide a default message if needed
    col_sections_text = (
        "\n\n".join(result.col_extraction.col_sections)
        if result.col_extraction.col_sections
        else "No Choice of Law sections were extracted from this case."
    )

    state = {
        # Case information
        "case_citation": result.case_citation,
        "full_text": result.metadata.get("case_text", ""),
        # Jurisdiction (already confirmed by user)
        "jurisdiction": result.jurisdiction_detection.legal_system_type,
        "precise_jurisdiction": result.jurisdiction_detection.precise_jurisdiction,
        # CoL sections - automatically extracted
        "col_section": [col_sections_text],
        "col_section_feedback": [],
        "col_first_score_submitted": True,
        "col_ready_edit": True,
        "col_done": True,
        # Themes - automatically classified
        "classification": [
            ", ".join(result.theme_classification.themes) if result.theme_classification.themes else "No themes classified"
        ],
        "theme_first_score_submitted": True,
        "theme_done": True,
        # Analysis results (ensure non-empty strings)
        "relevant_facts": [result.relevant_facts.facts if result.relevant_facts.facts else "No relevant facts extracted."],
        "pil_provisions": [result.pil_provisions.provisions if result.pil_provisions.provisions else []],
        "col_issue": [result.col_issue.issue if result.col_issue.issue else "No choice of law issue identified."],
        "courts_position": [
            result.courts_position.position if result.courts_position.position else "No court's position extracted."
        ],
        "abstract": [result.abstract.abstract if result.abstract.abstract else "No abstract generated."],
        # Common Law specific
        "obiter_dicta": [result.obiter_dicta.obiter_dicta] if result.obiter_dicta else [],
        "dissenting_opinions": [result.dissenting_opinions.dissenting_opinions] if result.dissenting_opinions else [],
        # Flags
        "analysis_ready": True,
        "analysis_done": True,
        # Metadata
        "username": result.metadata.get("username"),
        "user_email": result.metadata.get("user_email"),
        "model": result.metadata.get("model"),
        "analysis_timestamp": result.metadata.get("analysis_timestamp"),
        "duration_seconds": result.metadata.get("duration_seconds"),
        # Mark all steps as printed and scored
        "relevant_facts_printed": True,
        "relevant_facts_score_submitted": True,
        "pil_provisions_printed": True,
        "pil_provisions_score_submitted": True,
        "col_issue_printed": True,
        "col_issue_score_submitted": True,
        "courts_position_printed": True,
        "courts_position_score_submitted": True,
        "abstract_printed": True,
        "abstract_score_submitted": True,
    }

    # Add Common Law specific flags if applicable
    if result.obiter_dicta:
        state["obiter_dicta_printed"] = True
        state["obiter_dicta_score_submitted"] = True

    if result.dissenting_opinions:
        state["dissenting_opinions_printed"] = True
        state["dissenting_opinions_score_submitted"] = True

    return state


def render_agents_workflow_button(state):
    """
    Render button to trigger agents workflow after jurisdiction confirmation.

    Args:
        state: Current application state

    Returns:
        str or None: 'agents' if agents workflow selected, 'traditional' if traditional selected,
                     'waiting' if showing choice UI, None if choice already made
    """
    # Only show if jurisdiction is confirmed and agents workflow hasn't run yet
    # and traditional workflow hasn't progressed too far
    if (
        not state.get("agents_workflow_completed", False)
        and not state.get("col_extraction_started", False)
        and not state.get("col_done", False)
    ):
        st.markdown("---")
        st.markdown("### Choose Analysis Method")
        st.markdown("Please select how you would like to proceed with the analysis:")

        # Create two columns for the choice
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🤖 Automated Analysis")
            st.markdown(
                """
                **Fast & Efficient**: Uses OpenAI Agents workflow to automatically:
                - Extract Choice of Law sections
                - Classify PIL themes
                - Perform complete analysis
                
                ⚡ **50-67% faster** (60-90 seconds total)
                """
            )
            use_agents = st.button("Use Automated Analysis", type="primary", key="use_agents_workflow_btn")

        with col2:
            st.markdown("#### 👤 Step-by-Step Analysis")
            st.markdown(
                """
                **Interactive & Controlled**: Traditional workflow with human-in-the-loop at each step:
                - Review and edit CoL sections
                - Confirm theme classifications
                - Approve each analysis component
                
                🕐 Takes approximately 3-5 minutes
                """
            )
            use_traditional = st.button("Use Step-by-Step", key="use_traditional_workflow_btn")

        if use_agents:
            return "agents"
        elif use_traditional:
            return "traditional"
        else:
            # Return 'waiting' to indicate we're showing the choice UI and waiting for user input
            return "waiting"

    return None


def execute_agents_workflow(state):
    """
    Execute the agents workflow and update state.

    Args:
        state: Current application state
    """
    from utils.progress_banner import hide_progress_banner, show_progress_banner

    show_progress_banner("Running automated analysis with OpenAI Agents... This may take 60-90 seconds.")

    try:
        # Run agents workflow
        agents_result = run_agents_workflow(
            case_text=state.get("full_text", ""),
            case_citation=state.get("case_citation", ""),
            jurisdiction=state.get("jurisdiction", ""),
            precise_jurisdiction=state.get("precise_jurisdiction", ""),
            model=st.session_state.get("llm_model_select", "gpt-4o-mini"),
            username=st.session_state.get("user"),
            user_email=st.session_state.get("user_email"),
        )

        # Update state with results
        state.update(agents_result)
        state["agents_workflow_completed"] = True

        # Update session state
        st.session_state.col_state = state

        hide_progress_banner()

        # Show success message
        st.success("✅ Automated analysis complete! Review the results below.")

        # Force rerun to show results
        st.rerun()

    except Exception as e:
        hide_progress_banner()
        st.error(f"❌ Error during automated analysis: {str(e)}")
        logger.exception("Error in agents workflow")
