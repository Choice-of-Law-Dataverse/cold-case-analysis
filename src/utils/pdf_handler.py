import fitz  # fallback if needed
import pymupdf4llm


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from PDF using pymupdf4llm. Falls back to PyMuPDF directly if needed.
    :param uploaded_file: Uploaded file-like object from Streamlit
    :return: Extracted text as a string
    """
    try:
        # Read file bytes
        file_bytes = uploaded_file.read()
        # Use pymupdf4llm extraction
        text = pymupdf4llm.extract_text_from_pdf(file_bytes)
        return text
    except Exception:
        # Fallback to PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        return "\n".join(full_text)
