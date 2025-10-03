# components/jurisdiction_detection.py
"""
Streamlit component for enhanced jurisdiction detection with precise jurisdiction identification.
"""
import streamlit as st

from tools.jurisdiction_detector import detect_legal_system_type
from tools.precise_jurisdiction_detector import detect_precise_jurisdiction


def render_jurisdiction_detection(full_text: str):
    """
    Render the enhanced jurisdiction detection interface.

    Args:
        full_text: The court decision text to analyze

    Returns:
        bool: True if jurisdiction detection is complete and confirmed
    """

    # Initialize session state variables if not present
    if "precise_jurisdiction" not in st.session_state:
        st.session_state["precise_jurisdiction"] = None
    if "precise_jurisdiction_detected" not in st.session_state:
        st.session_state["precise_jurisdiction_detected"] = False
    if "legal_system_type" not in st.session_state:
        st.session_state["legal_system_type"] = None
    if "precise_jurisdiction_eval_score" not in st.session_state:
        st.session_state["precise_jurisdiction_eval_score"] = None
    if "precise_jurisdiction_confirmed" not in st.session_state:
        st.session_state["precise_jurisdiction_confirmed"] = False
    if "jurisdiction_manual_override" not in st.session_state:
        st.session_state["jurisdiction_manual_override"] = None

    # Phase 1: Detect Jurisdiction Button
    if not st.session_state["precise_jurisdiction_detected"]:
        detect_clicked = st.button("Detect Jurisdiction", key="detect_precise_jurisdiction_btn", type="primary")

        if detect_clicked:
            if full_text.strip():
                with st.spinner("Analyzing jurisdiction..."):
                    # Detect precise jurisdiction (now returns just the jurisdiction name)
                    jurisdiction_name = detect_precise_jurisdiction(full_text)

                    st.session_state["precise_jurisdiction"] = jurisdiction_name
                    st.session_state["precise_jurisdiction_detected"] = True

                    # Determine legal system type using the existing jurisdiction detection logic
                    legal_system = detect_legal_system_type(jurisdiction_name, full_text)

                    # Handle the case where the existing detector says "No court decision"
                    if legal_system == "No court decision":
                        legal_system = "Unknown legal system"

                    st.session_state["legal_system_type"] = legal_system

                    st.rerun()
            else:
                st.warning("Please enter the court decision text before detecting jurisdiction.")

        return False

    # Phase 2: Display Results and Override Options
    if st.session_state["precise_jurisdiction_detected"]:
        jurisdiction_name = st.session_state["precise_jurisdiction"]  # Now this is just a string
        legal_system = st.session_state["legal_system_type"]

        # Display results in an attractive format
        st.markdown("### Jurisdiction Detection Results")

        # Load all jurisdictions for selection
        from tools.precise_jurisdiction_detector import load_jurisdictions
        jurisdictions = load_jurisdictions()
        jurisdiction_names = [j["name"] for j in jurisdictions if j["name"]]

        # Find the index of the detected jurisdiction, default to first if not found
        try:
            default_jurisdiction_index = jurisdiction_names.index(jurisdiction_name) if jurisdiction_name in jurisdiction_names else 0
        except (ValueError, AttributeError):
            default_jurisdiction_index = 0

        selected_jurisdiction = st.selectbox(
            "Override with specific jurisdiction:",
            options=jurisdiction_names,
            index=default_jurisdiction_index,
            key="jurisdiction_manual_select",
            help="Select a different jurisdiction if the detection was incorrect"
        )

        # Legal system override
        legal_system_options = [
            "Civil-law jurisdiction",
            "Common-law jurisdiction",
            "Unknown legal system"
        ]

        # Find the index of the detected legal system, default to last (Unknown) if not found
        try:
            default_legal_system_index = legal_system_options.index(legal_system) if legal_system in legal_system_options else len(legal_system_options) - 1
        except (ValueError, AttributeError):
            default_legal_system_index = len(legal_system_options) - 1

        selected_legal_system = st.selectbox(
            "Override legal system classification:",
            options=legal_system_options,
            index=default_legal_system_index,
            key="legal_system_manual_select",
            help="Override the legal system classification if needed"
        )

        if st.button("Confirm", key="confirm_final_jurisdiction", type="primary"):
            # Update jurisdiction if changed
            if selected_jurisdiction != jurisdiction_name:
                # Find the selected jurisdiction data
                selected_data = next((j for j in jurisdictions if j["name"] == selected_jurisdiction), None)
                if selected_data:
                    st.session_state["jurisdiction_manual_override"] = {
                        "jurisdiction_name": selected_data["name"]
                    }
            
            # Update legal system if changed
            if selected_legal_system != legal_system:
                st.session_state["legal_system_type"] = selected_legal_system

            st.session_state["precise_jurisdiction_confirmed"] = True
            st.success("Jurisdiction detection completed and confirmed!")
            st.rerun()

    return st.session_state.get("precise_jurisdiction_confirmed", False)

def get_final_jurisdiction_data():
    """
    Get the final jurisdiction data after detection and confirmation.

    Returns:
        dict: Final jurisdiction information
    """
    if st.session_state.get("jurisdiction_manual_override"):
        # Use manual override data
        override_data = st.session_state["jurisdiction_manual_override"]
        return {
            "jurisdiction_name": override_data["jurisdiction_name"],
            "legal_system_type": st.session_state.get("legal_system_type"),
            "confidence": "manual_override",
            "evaluation_score": st.session_state.get("precise_jurisdiction_eval_score")
        }
    else:
        # Use detected data (now just a string)
        jurisdiction_name = st.session_state.get("precise_jurisdiction", "Unknown")
        return {
            "jurisdiction_name": jurisdiction_name,
            "legal_system_type": st.session_state.get("legal_system_type"),
            "confidence": "auto_detected",
            "evaluation_score": st.session_state.get("precise_jurisdiction_eval_score")
        }
