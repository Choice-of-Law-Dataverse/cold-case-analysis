# components/input_handler.py
"""
Input handling components for the CoLD Case Analyzer.
"""
import streamlit as st

from utils.pdf_handler import extract_text_from_pdf
from utils.state_manager import load_demo_case


def render_case_citation_input():
    """
    Render the case citation input field.

    Returns:
        str: The entered case citation
    """
    st.markdown("**Case Citation (required):**")
    st.caption(
        "This field should include the issuing court, party names (claimant/respondent), the official case or docket number, and the decision date. Citation styles differ by jurisdiction; use the native format. Examples — CH: Federal Court, 20.12.2005 - BGE 132 III 285; CAN: Nike Informatic Systems v Avac, 1979 CanLII 667 (British Columbia)."
    )
    return st.text_input(
        label="Case Citation",
        key="case_citation",
        placeholder="e.g., Federal Court, 20.12.2005 - BGE 132 III 285",
        label_visibility="collapsed",
    )


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


def render_pdf_uploader():
    """
    Render the PDF uploader and handle automatic text extraction.

    Returns:
        bool: True if PDF was successfully processed
    """
    pdf_file = st.file_uploader(
        "Or drag and drop a PDF file here:",
        type=["pdf"],
        key="pdf_upload",
        help="Upload a PDF to extract the full text automatically"
    )

    if pdf_file is not None:
        try:
            # Show progress banner while extracting
            banner_placeholder = st.empty()
            with banner_placeholder:
                st.markdown("""
                <div class="progress-banner">
                    <div class="progress-banner-content">
                        <div class="progress-banner-message">Extracting text from PDF...</div>
                        <div class="progress-banner-bar-container">
                            <svg viewBox="0 0 400 40" preserveAspectRatio="none">
                                <path d="M 0,20 Q 25,10 50,20 T 100,20 Q 125,30 150,20 T 200,20 Q 225,10 250,20 T 300,20 Q 325,30 350,20 T 400,20"
                                      stroke="rgba(255, 255, 255, 0.3)"
                                      stroke-width="3"
                                      fill="none"/>
                            </svg>
                            <div class='progress-banner-spinner'></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            extracted = extract_text_from_pdf(pdf_file)
            st.session_state.full_text_input = extracted

            # Clear the progress banner
            banner_placeholder.empty()
            st.success("Extracted text from PDF successfully.")
            return True
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {e}")
            return False

    return False


def render_text_input():
    """
    Render the main text input area for court decision text.

    Returns:
        str: The entered court decision text
    """
    # Ensure default session state for text input
    if "full_text_input" not in st.session_state:
        st.session_state.full_text_input = ""

    return st.text_area(
        "Paste the court decision text here:",
        height=200,
        help="Enter the full text of the court decision to extract the Choice of Law section.",
        key="full_text_input"
    )


def render_demo_button(full_text):
    """
    Render the demo case button if no text is entered.

    Args:
        full_text: Current text in the input area

    Returns:
        bool: True if demo button was shown and potentially clicked
    """
    if not full_text.strip():
        if st.button("Use Demo Case", on_click=load_demo_case, key="demo_button"):
            return True
    return False


def render_input_phase():
    """
    Render the complete input phase (citation, PDF, text, demo).

    Returns:
        tuple: (case_citation, full_text) - the citation and decision text
    """
    render_email_input()
    case_citation = render_case_citation_input()
    render_pdf_uploader()
    full_text = render_text_input()
    render_demo_button(full_text)

    return case_citation, full_text
