# components/analysis_manager.py
"""
UI component for managing multiple analyses.
"""
import logging
from datetime import datetime

import streamlit as st

logger = logging.getLogger(__name__)


def render_analysis_manager():
    """Render the analysis manager UI in the sidebar."""
    from utils.browser_storage import (
        create_new_analysis,
        delete_analysis,
        get_current_analysis_id,
        list_analyses,
        load_analysis_state,
        set_current_analysis_id,
    )

    st.markdown("### 📁 My Analyses")

    analyses = list_analyses()
    current_id = get_current_analysis_id() or st.session_state.get("current_analysis_id")

    if not analyses:
        st.info("No saved analyses yet. Start a new analysis to save it.")
        return

    # Display analyses
    for _idx, analysis in enumerate(analyses):
        analysis_id = analysis["id"]
        case_citation = analysis.get("case_citation", "Untitled")
        created_at = datetime.fromtimestamp(analysis.get("created_at", 0))
        submitted_at = analysis.get("submitted_at")

        # Determine if this is the current analysis
        is_current = analysis_id == current_id

        # Create a container for each analysis
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                # Display analysis info
                citation_display = case_citation[:30] + "..." if len(case_citation) > 30 else case_citation
                status_icon = "✅" if submitted_at else "📝"
                current_marker = "**→**" if is_current else ""

                st.markdown(f"{current_marker} {status_icon} **ID: {analysis_id}**")
                st.caption(f"{citation_display}")
                st.caption(f"Created: {created_at.strftime('%Y-%m-%d %H:%M')}")

                if submitted_at:
                    submit_time = datetime.fromtimestamp(submitted_at)
                    st.caption(f"✓ Submitted: {submit_time.strftime('%Y-%m-%d %H:%M')}")

            with col2:
                # Load button
                if st.button("Load", key=f"load_{analysis_id}", disabled=is_current):
                    try:
                        # Set as current
                        set_current_analysis_id(analysis_id)
                        st.session_state["current_analysis_id"] = analysis_id

                        # Load state
                        analysis_state = load_analysis_state(analysis_id)
                        if analysis_state:
                            for key, value in analysis_state.items():
                                st.session_state[key] = value

                        st.success(f"Loaded analysis {analysis_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading analysis: {e}")
                        logger.error(f"Error loading analysis {analysis_id}: {e}")

            with col3:
                # Delete button
                if st.button("🗑️", key=f"delete_{analysis_id}"):
                    try:
                        delete_analysis(analysis_id)

                        # If this was current, clear session
                        if is_current:
                            # Clear analysis-related session state
                            from utils.state_manager import clear_analysis_state_only

                            clear_analysis_state_only()

                        st.success(f"Deleted analysis {analysis_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting analysis: {e}")
                        logger.error(f"Error deleting analysis {analysis_id}: {e}")

            st.divider()

    # New analysis button
    if st.button("➕ New Analysis", key="new_analysis_btn", use_container_width=True):
        try:
            new_id = create_new_analysis()
            st.session_state["current_analysis_id"] = new_id

            # Clear current session state for new analysis
            from utils.state_manager import clear_analysis_state_only

            clear_analysis_state_only()

            st.success(f"Created new analysis: {new_id}")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating new analysis: {e}")
            logger.error(f"Error creating new analysis: {e}")
