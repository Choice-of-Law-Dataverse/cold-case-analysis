"""PDF text extraction using pymupdf4llm."""

import logging
from io import BytesIO
from typing import Any, BinaryIO, Protocol, cast

import fitz  # type: ignore[import-untyped]
import pymupdf  # type: ignore[import-untyped]
import pymupdf4llm

from utils.azure_storage import is_azure_storage_configured, upload_pdf_to_azure

logger = logging.getLogger(__name__)


class SupportsRead(Protocol):
    def read(self, size: int | None = None) -> bytes: ...

    def seek(self, offset: int, whence: int = 0) -> int: ...


def extract_text_from_pdf(uploaded_file: SupportsRead | BinaryIO) -> str:
    """
    Extract text from PDF using pymupdf4llm.

    Also uploads to Azure Blob Storage if configured and stores metadata.

    :param uploaded_file: Uploaded file-like object from Streamlit
    :return: Extracted text as a string
    """
    # Get original filename if available
    original_filename = getattr(uploaded_file, "name", None)

    # Read file bytes once so we can both upload and extract
    file_bytes = uploaded_file.read()

    # Try to upload to Azure Blob Storage if configured
    try:
        if is_azure_storage_configured():
            # Create a BytesIO object for upload
            upload_file = BytesIO(file_bytes)

            azure_result = upload_pdf_to_azure(upload_file, original_filename=original_filename)
            if azure_result:
                # Store PDF metadata in session state if Streamlit is available
                try:
                    import streamlit as st

                    st.session_state.pdf_url = azure_result["url"]
                    st.session_state.pdf_uuid = azure_result["uuid"]
                    st.session_state.pdf_filename = azure_result["filename"]
                    logger.info(f"Uploaded PDF to Azure with UUID {azure_result['uuid']}")
                except (ImportError, RuntimeError):
                    logger.debug("Streamlit session state not available")
        else:
            logger.debug("Azure Storage not configured, skipping upload")
    except Exception as e:
        logger.warning(f"Failed to upload PDF to Azure Storage: {e}")

    # Extract text using pymupdf4llm
    try:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:  # type: ignore[attr-defined]
            result = pymupdf4llm.to_markdown(doc)
            # to_markdown can return str or list of dicts, we need str
            if isinstance(result, str):
                return result
            # If it returns a list of dicts, extract text from them
            if isinstance(result, list):
                return "\n".join(str(item) for item in result)
            return str(result)
    except Exception:
        # Fallback to PyMuPDF directly
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:  # type: ignore[attr-defined]
            lines: list[str] = []
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                lines.append(str(cast(Any, page).get_text()))
            return "\n".join(lines)
