"""
utils.py
--------
Helper utilities: text extraction from PDF, DOCX, and plain text.
"""

import io
import pymupdf        # PyMuPDF >= 1.24 (replaces deprecated `import fitz`)
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file given its raw bytes."""
    text_parts = []
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all paragraph text from a .docx file given its raw bytes."""
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]
    return "\n".join(paragraphs).strip()


def chunk_text(text: str, max_chars: int = 3000) -> list[str]:
    """
    Split text into chunks of at most max_chars characters,
    breaking at paragraph boundaries where possible.
    """
    paragraphs = text.split("\n")
    chunks, current = [], []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current, current_len = [], 0
        current.append(para)
        current_len += len(para) + 1

    if current:
        chunks.append("\n".join(current))

    return chunks
