# components/input_handler.py
"""
Input handling components for the CoLD Case Analyzer.
"""

import logging

import streamlit as st

from utils.pdf_handler import extract_text_from_pdf

logger = logging.getLogger(__name__)


def render_pdf_uploader():
    """
    Render the PDF uploader and handle automatic text extraction.
    Also uploads the PDF to Azure Blob Storage if configured.

    Returns:
        bool: True if PDF was successfully processed
    """
    pdf_file = st.file_uploader(
        "Or drag and drop a PDF file here:",
        type=["pdf"],
        key="pdf_upload",
        help="Upload a PDF to extract the full text automatically",
        label_visibility="collapsed",
    )

    if pdf_file is not None:
        try:
            # Extract text from PDF (automatically uploads to Azure and uses Document Intelligence)
            extracted = extract_text_from_pdf(pdf_file)
            st.session_state.full_text_input = extracted

            # Store PDF metadata if available from upload
            # Note: upload_pdf_to_azure is called internally by extract_text_from_pdf
            st.success("Extracted text from PDF successfully.")
            return True
        except Exception as e:
            st.error(f"Failed to extract text from PDF: {e}")
            logger.error(f"PDF processing error: {e}", exc_info=True)
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
        "Or paste the court decision text here:",
        height=200,
        help="Enter the full text of the court decision to extract the Choice of Law section.",
        key="full_text_input",
    )


def render_input_phase():
    """
    Render the complete input phase (citation, PDF, text, demo).

    Returns:
        tuple: (case_citation, full_text) - the citation and decision text
    """
    detection_started = st.session_state.get("jurisdiction_detect_clicked", False)

    if not detection_started:
        render_pdf_uploader()
        full_text = render_text_input()
    else:
        full_text = st.session_state.get("full_text_input", "")

    return full_text
