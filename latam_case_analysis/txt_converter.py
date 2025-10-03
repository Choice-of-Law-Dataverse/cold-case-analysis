#!/usr/bin/env python3
"""
Converts all PDFs in the 'pdfs' folder to text files in the 'txts' folder using pymupdf4llm.
"""

import os

try:
    import fitz  # for fallback extraction
    import pymupdf4llm
except ImportError as e:
    raise ImportError("Missing required packages: pymupdf4llm and fitz") from e

# Directories relative to this script
def get_dirs():
    base = os.path.dirname(__file__)
    return os.path.join(base, "pdfs"), os.path.join(base, "txts")


def convert_pdf_to_txt(pdf_path: str, txt_path: str):
    """
    Convert a single PDF to text using pymupdf4llm with fallback to fitz.
    """
    # Read file bytes
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()
    try:
        # Use pymupdf4llm extraction
        text = pymupdf4llm.extract_text_from_pdf(file_bytes)
    except Exception:
        # Fallback to PyMuPDF via fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts = [page.get_text() for page in doc]
        text = "\n".join(texts)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    pdf_dir, txt_dir = get_dirs()
    os.makedirs(txt_dir, exist_ok=True)

    for fname in os.listdir(pdf_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(pdf_dir, fname)
        txt_name = os.path.splitext(fname)[0] + ".txt"
        txt_path = os.path.join(txt_dir, txt_name)
        print(f"Converting {fname} -> {txt_name}")
        try:
            convert_pdf_to_txt(pdf_path, txt_path)
        except Exception as e:
            print(f"Error processing {fname}: {e}")

    print("Conversion complete.")


if __name__ == "__main__":
    main()
