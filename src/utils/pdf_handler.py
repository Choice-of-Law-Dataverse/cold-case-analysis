from typing import Any, BinaryIO, Protocol, cast

import fitz  # type: ignore[import-untyped]
import pymupdf  # type: ignore[import-untyped]
import pymupdf4llm


class SupportsRead(Protocol):
    def read(self, size: int | None = None) -> bytes:
        ...


def extract_text_from_pdf(uploaded_file: SupportsRead | BinaryIO) -> str:
    """
    Extract text from PDF using pymupdf4llm. Falls back to PyMuPDF directly if needed.
    :param uploaded_file: Uploaded file-like object from Streamlit
    :return: Extracted text as a string
    """
    # Read file bytes once so the fallback can reuse them
    file_bytes = uploaded_file.read()

    try:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:  # type: ignore[attr-defined]
            return pymupdf4llm.to_markdown(doc)
    except Exception:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:  # type: ignore[attr-defined]
            lines: list[str] = []
            for page_index in range(doc.page_count):
                page = doc.load_page(page_index)
                lines.append(str(cast(Any, page).get_text()))
            return "\n".join(lines)
