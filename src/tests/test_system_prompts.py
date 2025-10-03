# tests/test_system_prompts.py
"""
Test utilities for verifying dynamic system prompts functionality.
"""
import sys
from pathlib import Path

# Add the parent directory (streamlit) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from utils.system_prompt_generator import generate_jurisdiction_specific_prompt, load_jurisdiction_summaries


def render_system_prompt_preview():
    """
    Render a preview of the dynamic system prompt based on current jurisdiction detection.
    This is for testing and demonstration purposes.
    """
    st.markdown("### 🧪 Dynamic System Prompt Preview")

    # Get jurisdiction information from session state
    jurisdiction_name = None
    legal_system_type = None

    if hasattr(st.session_state, "precise_jurisdiction"):
        jurisdiction_name = st.session_state.precise_jurisdiction
    if hasattr(st.session_state, "legal_system_type"):
        legal_system_type = st.session_state.legal_system_type

    # Show current jurisdiction info
    if jurisdiction_name or legal_system_type:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Detected Jurisdiction:** {jurisdiction_name or 'Unknown'}")
        with col2:
            st.write(f"**Legal System:** {legal_system_type or 'Unknown'}")

        # Generate the system prompt
        system_prompt = generate_jurisdiction_specific_prompt(jurisdiction_name, legal_system_type)

        # Display the system prompt in an expandable section
        with st.expander("📝 Generated System Prompt", expanded=False):
            st.text_area(
                "System Prompt for AI Model:",
                value=system_prompt,
                height=300,
                disabled=True
            )

        # Load and display jurisdiction summaries for verification
        summaries = load_jurisdiction_summaries()
        if jurisdiction_name and jurisdiction_name in summaries:
            with st.expander("ℹ️ Jurisdiction Summary Used", expanded=False):
                st.text_area(
                    f"Summary for {jurisdiction_name}:",
                    value=summaries[jurisdiction_name],
                    height=150,
                    disabled=True
                )
        elif jurisdiction_name and jurisdiction_name != "Unknown":
            st.info(f"No specific jurisdiction summary found for {jurisdiction_name}")
    else:
        st.info("No jurisdiction detected yet. Complete jurisdiction detection to see the dynamic system prompt.")


def render_manual_system_prompt_test():
    """
    Render a manual test interface for system prompt generation.
    """
    st.markdown("### 🔧 Manual System Prompt Testing")

    # Manual input fields
    col1, col2 = st.columns(2)

    with col1:
        test_jurisdiction = st.selectbox(
            "Test Jurisdiction:",
            ["", "Germany", "United States", "India", "France", "China (Mainland)", "Brazil", "Unknown"],
            key="test_jurisdiction"
        )

    with col2:
        test_legal_system = st.selectbox(
            "Test Legal System:",
            ["", "Civil-law jurisdiction", "Common-law jurisdiction", "Unknown legal system"],
            key="test_legal_system"
        )

    if st.button("Generate Test Prompt", key="generate_test_prompt"):
        if test_jurisdiction or test_legal_system:
            system_prompt = generate_jurisdiction_specific_prompt(
                test_jurisdiction if test_jurisdiction else None,
                test_legal_system if test_legal_system else None
            )

            st.markdown("**Generated System Prompt:**")
            st.text_area(
                "Test System Prompt:",
                value=system_prompt,
                height=400,
                disabled=True,
                key="test_prompt_display"
            )
        else:
            st.warning("Please select at least one parameter to test.")


def show_available_jurisdictions():
    """
    Display all available jurisdictions with summaries.
    """
    st.markdown("### 📊 Available Jurisdictions with Summaries")

    summaries = load_jurisdiction_summaries()

    if summaries:
        st.write(f"**Total jurisdictions with summaries:** {len(summaries)}")

        # Create a searchable list
        search_term = st.text_input("Search jurisdictions:", key="search_jurisdictions")

        filtered_summaries = summaries
        if search_term:
            filtered_summaries = {
                name: summary for name, summary in summaries.items()
                if search_term.lower() in name.lower()
            }

        # Display in expandable sections
        for jurisdiction, summary in filtered_summaries.items():
            with st.expander(f"🌍 {jurisdiction}"):
                st.text_area(
                    "Summary:",
                    value=summary,
                    height=100,
                    disabled=True,
                    key=f"summary_{jurisdiction}"
                )
    else:
        st.error("No jurisdiction summaries could be loaded. Please check the jurisdictions.csv file.")
