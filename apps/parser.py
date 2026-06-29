# app/parser.py

import fitz          # PyMuPDF
import docx
import os

def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}")
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract all text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        raise ValueError(f"Could not read DOCX: {e}")
    return text.strip()


def extract_text(file_path: str) -> str:
    """
    Auto-detect file type and extract text.
    Supports .pdf and .docx only.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .docx")


def load_job_description(source: str) -> str:
    """
    Load a job description from either:
    - a .txt file path
    - a raw string pasted directly
    """
    # If it looks like a file path and the file exists, read it
    if os.path.exists(source) and source.endswith(".txt"):
        with open(source, "r", encoding="utf-8") as f:
            return f.read().strip()
    # Otherwise treat it as raw text
    return source.strip()