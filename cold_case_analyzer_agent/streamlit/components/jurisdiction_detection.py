# components/jurisdiction_detection.py
"""
Streamlit component for enhanced jurisdiction detection with precise jurisdiction identification.
"""
import streamlit as st
from tools.precise_jurisdiction_detector import detect_precise_jurisdiction, determine_legal_system_type

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
    if "jurisdiction_confidence" not in st.session_state:
        st.session_state["jurisdiction_confidence"] = None
    if "jurisdiction_reasoning" not in st.session_state:
        st.session_state["jurisdiction_reasoning"] = None
    if "precise_jurisdiction_eval_score" not in st.session_state:
        st.session_state["precise_jurisdiction_eval_score"] = None
    if "precise_jurisdiction_eval_submitted" not in st.session_state:
        st.session_state["precise_jurisdiction_eval_submitted"] = False
    if "precise_jurisdiction_confirmed" not in st.session_state:
        st.session_state["precise_jurisdiction_confirmed"] = False
    if "jurisdiction_manual_override" not in st.session_state:
        st.session_state["jurisdiction_manual_override"] = None

    # Phase 1: Detect Jurisdiction Button
    if not st.session_state["precise_jurisdiction_detected"]:
        detect_clicked = st.button("🔍 Detect Precise Jurisdiction", key="detect_precise_jurisdiction_btn", type="primary")
        
        if detect_clicked:
            if full_text.strip():
                with st.spinner("Analyzing jurisdiction..."):
                    # Detect precise jurisdiction
                    jurisdiction_result = detect_precise_jurisdiction(full_text)
                    
                    st.session_state["precise_jurisdiction"] = jurisdiction_result
                    st.session_state["precise_jurisdiction_detected"] = True
                    
                    # Determine legal system type if jurisdiction was identified
                    if (jurisdiction_result["jurisdiction_name"] and 
                        jurisdiction_result["jurisdiction_name"] != "Unknown"):
                        legal_system = determine_legal_system_type(
                            jurisdiction_result["jurisdiction_name"],
                            jurisdiction_result["jurisdiction_code"] or "",
                            jurisdiction_result.get("jurisdiction_summary", "")
                        )
                        st.session_state["legal_system_type"] = legal_system
                    else:
                        st.session_state["legal_system_type"] = "Unknown legal system"
                    
                    st.session_state["jurisdiction_confidence"] = jurisdiction_result["confidence"]
                    st.session_state["jurisdiction_reasoning"] = jurisdiction_result["reasoning"]
                    
                    st.rerun()
            else:
                st.warning("Please enter the court decision text before detecting jurisdiction.")
                
        return False

    # Phase 2: Display Results and Evaluation
    if st.session_state["precise_jurisdiction_detected"]:
        jurisdiction_data = st.session_state["precise_jurisdiction"]
        
        # Display results in an attractive format
        st.markdown("### 🏛️ Jurisdiction Detection Results")
        
        # Create columns for better layout
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if jurisdiction_data["jurisdiction_name"] != "Unknown":
                st.markdown(f"**Jurisdiction:** {jurisdiction_data['jurisdiction_name']}")
                if jurisdiction_data["jurisdiction_code"]:
                    st.markdown(f"**Code:** {jurisdiction_data['jurisdiction_code']}")
            else:
                st.markdown("**Jurisdiction:** ❌ Could not identify specific jurisdiction")
        
        with col2:
            confidence_color = {
                "high": "🟢",
                "medium": "🟡", 
                "low": "🔴"
            }.get(st.session_state["jurisdiction_confidence"], "⚪")
            st.markdown(f"**Confidence:** {confidence_color} {st.session_state['jurisdiction_confidence']}")
        
        with col3:
            legal_system = st.session_state["legal_system_type"]
            system_icon = {
                "Civil-law jurisdiction": "⚖️",
                "Common-law jurisdiction": "🏛️",
                "Mixed or unclear legal system": "🔀",
                "Unknown legal system": "❓"
            }.get(legal_system, "❓")
            st.markdown(f"**Legal System:** {system_icon} {legal_system}")
        
        # Show reasoning
        with st.expander("📝 Detection Reasoning", expanded=False):
            st.write(st.session_state["jurisdiction_reasoning"])
        
        # Show jurisdiction summary if available
        if (jurisdiction_data.get("jurisdiction_summary") and 
            jurisdiction_data["jurisdiction_summary"].strip()):
            with st.expander("📚 Jurisdiction Legal Framework", expanded=False):
                st.write(jurisdiction_data["jurisdiction_summary"])

        # Phase 3: Evaluation
        if not st.session_state["precise_jurisdiction_eval_submitted"]:
            st.markdown("### 📊 Evaluate Detection Accuracy")
            score = st.slider(
                "How accurate is this jurisdiction identification? (0-100)",
                min_value=0, max_value=100, value=85, step=1,
                key="precise_jurisdiction_eval_slider",
                help="Rate the accuracy of both the specific jurisdiction and legal system identification"
            )
            
            if st.button("Submit Evaluation", key="submit_precise_jurisdiction_eval"):
                st.session_state["precise_jurisdiction_eval_score"] = score
                st.session_state["precise_jurisdiction_eval_submitted"] = True
                st.rerun()
        else:
            # Show evaluation score
            score = st.session_state["precise_jurisdiction_eval_score"]
            score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
            st.markdown(f"**Your Evaluation:** {score_color} {score}/100")

        # Phase 4: Manual Override Option
        if st.session_state["precise_jurisdiction_eval_submitted"]:
            st.markdown("### ✏️ Manual Override (Optional)")
            
            # Load all jurisdictions for selection
            from tools.precise_jurisdiction_detector import load_jurisdictions
            jurisdictions = load_jurisdictions()
            jurisdiction_names = ["Keep Current Detection"] + [j['name'] for j in jurisdictions if j['name']]
            
            selected_jurisdiction = st.selectbox(
                "Override with specific jurisdiction:",
                options=jurisdiction_names,
                index=0,
                key="jurisdiction_manual_select",
                help="Select a different jurisdiction if the detection was incorrect"
            )
            
            # Legal system override
            legal_system_options = [
                "Keep Current Detection",
                "Civil-law jurisdiction", 
                "Common-law jurisdiction",
                "Mixed or unclear legal system",
                "Unknown legal system"
            ]
            
            selected_legal_system = st.selectbox(
                "Override legal system classification:",
                options=legal_system_options,
                index=0,
                key="legal_system_manual_select",
                help="Override the legal system classification if needed"
            )
            
            if st.button("Confirm Final Jurisdiction", key="confirm_final_jurisdiction", type="primary"):
                # Apply overrides if selected
                if selected_jurisdiction != "Keep Current Detection":
                    # Find the selected jurisdiction data
                    selected_data = next((j for j in jurisdictions if j['name'] == selected_jurisdiction), None)
                    if selected_data:
                        st.session_state["jurisdiction_manual_override"] = {
                            "jurisdiction_name": selected_data['name'],
                            "jurisdiction_code": selected_data['code'],
                            "jurisdiction_summary": selected_data['summary']
                        }
                
                if selected_legal_system != "Keep Current Detection":
                    st.session_state["legal_system_type"] = selected_legal_system
                
                st.session_state["precise_jurisdiction_confirmed"] = True
                st.success("✅ Jurisdiction detection completed and confirmed!")
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
            "jurisdiction_code": override_data["jurisdiction_code"],
            "legal_system_type": st.session_state.get("legal_system_type"),
            "jurisdiction_summary": override_data.get("jurisdiction_summary"),
            "confidence": "manual_override",
            "evaluation_score": st.session_state.get("precise_jurisdiction_eval_score")
        }
    else:
        # Use detected data
        jurisdiction_data = st.session_state.get("precise_jurisdiction", {})
        return {
            "jurisdiction_name": jurisdiction_data.get("jurisdiction_name"),
            "jurisdiction_code": jurisdiction_data.get("jurisdiction_code"),
            "legal_system_type": st.session_state.get("legal_system_type"),
            "jurisdiction_summary": jurisdiction_data.get("jurisdiction_summary"),
            "confidence": st.session_state.get("jurisdiction_confidence"),
            "evaluation_score": st.session_state.get("precise_jurisdiction_eval_score")
        }
