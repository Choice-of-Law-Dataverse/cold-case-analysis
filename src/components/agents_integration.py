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
        # Metadata
        "username": result.metadata.get("username"),
        "user_email": result.metadata.get("user_email"),
        "model": result.metadata.get("model"),
        "analysis_timestamp": result.metadata.get("analysis_timestamp"),
        "duration_seconds": result.metadata.get("duration_seconds"),
    }

    # Add Common Law specific flags if applicable
    if result.obiter_dicta:
        state["obiter_dicta_printed"] = True
        state["obiter_dicta_score_submitted"] = True

    if result.dissenting_opinions:
        state["dissenting_opinions_printed"] = True
        state["dissenting_opinions_score_submitted"] = True

    return state


def execute_agents_workflow(state):
    """
    Execute the agents workflow and update state.

    Args:
        state: Current application state
    """
    from utils.progress_banner import hide_progress_banner, show_progress_banner

    show_progress_banner("⏳ Running automated analysis with OpenAI Agents... This may take 60-90 seconds.")

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
        st.success("✅ Automated analysis complete! Review and edit the results below, then submit.")

        # Force rerun to show results
        st.rerun()

    except Exception as e:
        hide_progress_banner()
        st.error(f"❌ Error during automated analysis: {str(e)}")
        logger.exception("Error in agents workflow")


def render_agents_results(state):
    """
    Render the agents workflow results in an editable format.
    
    Args:
        state: Current application state with agents results
    """
    st.markdown("## Analysis Results")
    st.markdown("Review and edit the automated analysis results below. When satisfied, click Submit to save.")
    
    # CoL Sections
    st.markdown("### Choice of Law Sections")
    col_section = st.text_area(
        "Extracted Choice of Law sections",
        value=state.get("col_section", [""])[0],
        height=200,
        key="agents_col_section_edit"
    )
    state["col_section"] = [col_section]
    
    # Themes
    st.markdown("### PIL Themes")
    classification = st.text_area(
        "Classified PIL themes",
        value=state.get("classification", [""])[0],
        height=100,
        key="agents_themes_edit"
    )
    state["classification"] = [classification]
    
    # Abstract
    st.markdown("### Abstract")
    abstract = st.text_area(
        "Case abstract",
        value=state.get("abstract", [""])[0],
        height=150,
        key="agents_abstract_edit"
    )
    state["abstract"] = [abstract]
    
    # Relevant Facts
    st.markdown("### Relevant Facts")
    relevant_facts = st.text_area(
        "Relevant facts",
        value=state.get("relevant_facts", [""])[0],
        height=200,
        key="agents_facts_edit"
    )
    state["relevant_facts"] = [relevant_facts]
    
    # PIL Provisions
    st.markdown("### PIL Provisions")
    pil_provisions_value = state.get("pil_provisions", [[]])[0]
    if isinstance(pil_provisions_value, list):
        pil_provisions_str = "\n".join(pil_provisions_value) if pil_provisions_value else ""
    else:
        pil_provisions_str = str(pil_provisions_value)
    
    pil_provisions = st.text_area(
        "PIL provisions (one per line)",
        value=pil_provisions_str,
        height=150,
        key="agents_provisions_edit"
    )
    state["pil_provisions"] = [[line.strip() for line in pil_provisions.split("\n") if line.strip()]]
    
    # CoL Issue
    st.markdown("### Choice of Law Issue")
    col_issue = st.text_area(
        "Choice of Law issue",
        value=state.get("col_issue", [""])[0],
        height=150,
        key="agents_issue_edit"
    )
    state["col_issue"] = [col_issue]
    
    # Court's Position
    st.markdown("### Court's Position")
    courts_position = st.text_area(
        "Court's position",
        value=state.get("courts_position", [""])[0],
        height=200,
        key="agents_position_edit"
    )
    state["courts_position"] = [courts_position]
    
    # Common Law specific (if applicable)
    if state.get("obiter_dicta"):
        st.markdown("### Obiter Dicta")
        obiter_dicta = st.text_area(
            "Obiter dicta",
            value=state.get("obiter_dicta", [""])[0],
            height=150,
            key="agents_obiter_edit"
        )
        state["obiter_dicta"] = [obiter_dicta]
    
    if state.get("dissenting_opinions"):
        st.markdown("### Dissenting Opinions")
        dissenting_opinions = st.text_area(
            "Dissenting opinions",
            value=state.get("dissenting_opinions", [""])[0],
            height=150,
            key="agents_dissenting_edit"
        )
        state["dissenting_opinions"] = [dissenting_opinions]
    
    # Update session state
    st.session_state.col_state = state
    
    # Submit button
    st.markdown("---")
    if st.button("Submit Analysis", type="primary", key="submit_agents_analysis"):
        from components.database import save_analysis_to_database
        
        try:
            save_analysis_to_database(state)
            st.success("✅ Analysis saved successfully!")
        except Exception as e:
            st.error(f"❌ Error saving analysis: {str(e)}")
            logger.exception("Error saving analysis")
