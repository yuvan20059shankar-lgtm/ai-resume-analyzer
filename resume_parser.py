"""
Resume Parser Module
Safely extracts raw text from PDF, DOCX, and TXT files.
Uses a dual-engine PDF extraction pipeline (pdfplumber + pypdf) to handle complex layouts,
two-column resumes, and tables, with graceful fallbacks for scanned/image-only PDFs.
"""

import io
import os
from typing import Dict, Any, Union, Optional
import docx
from pypdf import PdfReader

# Try importing pdfplumber for enhanced multi-column and table extraction
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


def extract_from_pdf(file_source: Union[str, io.BytesIO, bytes]) -> Dict[str, Any]:
    """
    Extracts text and page metadata from a PDF file using a dual-engine approach:
      1. Tries pdfplumber first (best for tables, two-column layouts, font encodings).
      2. Falls back to or complements with pypdf (lightweight and robust).
      3. Gracefully detects scanned/image-only PDFs and returns clean status and advice.

    Args:
        file_source: File path (str), raw bytes, or BytesIO stream.

    Returns:
        Dict with keys: success, text, page_count, word_count, file_type, is_scanned, error, suggestion
    """
    # Normalize input into bytes so we can seek and pass to multiple readers safely
    raw_bytes: Optional[bytes] = None
    if isinstance(file_source, bytes):
        raw_bytes = file_source
    elif isinstance(file_source, str):
        if not os.path.exists(file_source):
            return {
                "success": False,
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "file_type": "PDF",
                "is_scanned": False,
                "error": f"File does not exist: {file_source}",
                "suggestion": "Please check the file path and try again.",
            }
        try:
            with open(file_source, "rb") as f:
                raw_bytes = f.read()
        except Exception as read_err:
            return {
                "success": False,
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "file_type": "PDF",
                "is_scanned": False,
                "error": f"Cannot read file: {read_err}",
                "suggestion": "Ensure the file is not locked or corrupted.",
            }
    elif hasattr(file_source, "read"):
        current_pos = file_source.tell() if hasattr(file_source, "tell") else 0
        raw_bytes = file_source.read()
        if hasattr(file_source, "seek"):
            file_source.seek(current_pos)
    elif isinstance(file_source, io.BytesIO):
        raw_bytes = file_source.getvalue()

    if not raw_bytes or len(raw_bytes) < 10:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "word_count": 0,
            "file_type": "PDF",
            "is_scanned": False,
            "error": "The uploaded PDF file is empty (0 bytes).",
            "suggestion": "Please select a valid PDF resume file.",
        }

    page_count = 0
    extracted_text_plumber = ""
    extracted_text_pypdf = ""

    # Engine 1: pdfplumber (Handles tables, layout blocks, multi-column resumes)
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                page_count = len(pdf.pages)
                page_texts = []
                for p in pdf.pages:
                    # 1. Standard page text
                    p_txt = p.extract_text(layout=True) or p.extract_text() or ""
                    if p_txt.strip():
                        page_texts.append(p_txt.strip())

                    # 2. Extract tables (resumes often put skills in tables)
                    try:
                        tables = p.extract_tables()
                        for t in tables:
                            for row in t:
                                row_cells = [str(c).strip() for c in row if c and str(c).strip()]
                                if row_cells:
                                    page_texts.append(" | ".join(row_cells))
                    except Exception:
                        pass
                extracted_text_plumber = "\n".join(page_texts).strip()
        except Exception:
            # Fall through to pypdf
            pass

    # Engine 2: pypdf (Fast, handles encrypted or edge-case PDF streams)
    try:
        reader = PdfReader(io.BytesIO(raw_bytes))
        if page_count == 0:
            page_count = len(reader.pages)

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception as decrypt_err:
                return {
                    "success": False,
                    "text": "",
                    "page_count": page_count,
                    "word_count": 0,
                    "file_type": "PDF",
                    "is_scanned": False,
                    "error": f"The PDF is password protected: {decrypt_err}",
                    "suggestion": "Please remove the password protection from your resume PDF and re-upload.",
                }

        page_texts_pypdf = []
        for idx, page in enumerate(reader.pages):
            try:
                txt = page.extract_text()
                if txt and txt.strip():
                    page_texts_pypdf.append(txt.strip())
            except Exception:
                pass
        extracted_text_pypdf = "\n".join(page_texts_pypdf).strip()
    except Exception:
        pass

    # Choose the richer extraction (whichever captured more words)
    words_plumber = len(extracted_text_plumber.split())
    words_pypdf = len(extracted_text_pypdf.split())

    best_text = extracted_text_plumber if words_plumber >= words_pypdf else extracted_text_pypdf
    final_word_count = len(best_text.split())

    # Detect if PDF is a scanned image (has pages, but no extractable textual characters)
    if final_word_count < 5:
        return {
            "success": False,
            "text": "",
            "page_count": max(page_count, 1),
            "word_count": 0,
            "file_type": "PDF",
            "is_scanned": True,
            "error": "Scanned or Image-Based PDF: No selectable text layer was detected.",
            "suggestion": (
                "This PDF appears to be a scanned document or contains only flattened images. "
                "You can paste your resume text directly into the text box below, "
                "or upload a digital PDF/DOCX exported directly from Word, Google Docs, or Canva."
            ),
        }

    return {
        "success": True,
        "text": best_text,
        "page_count": page_count,
        "word_count": final_word_count,
        "file_type": "PDF",
        "is_scanned": False,
        "error": None,
        "suggestion": None,
    }


def extract_from_docx(file_source: Union[str, io.BytesIO, bytes]) -> Dict[str, Any]:
    """
    Extracts text from a DOCX document including body paragraphs and table contents.

    Args:
        file_source: File path (str), raw bytes, or BytesIO stream.

    Returns:
        Dict with keys: success, text, page_count, word_count, file_type, is_scanned, error, suggestion
    """
    try:
        if isinstance(file_source, bytes):
            stream = io.BytesIO(file_source)
        elif isinstance(file_source, str):
            if not os.path.exists(file_source):
                return {
                    "success": False,
                    "text": "",
                    "page_count": 0,
                    "word_count": 0,
                    "file_type": "DOCX",
                    "is_scanned": False,
                    "error": f"File does not exist: {file_source}",
                    "suggestion": "Please check the file path.",
                }
            stream = file_source
        else:
            stream = file_source

        doc = docx.Document(stream)
        extracted_lines = []

        # 1. Paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                extracted_lines.append(text)

        # 2. Tables
        for table in doc.tables:
            for row in table.rows:
                row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if row_cells:
                    extracted_lines.append(" | ".join(row_cells))

        full_text = "\n".join(extracted_lines).strip()
        word_count = len(full_text.split())

        if word_count < 5:
            return {
                "success": False,
                "text": "",
                "page_count": 1,
                "word_count": 0,
                "file_type": "DOCX",
                "is_scanned": True,
                "error": "The DOCX document contains no readable text content.",
                "suggestion": "Please upload a document with text content, or paste your resume text below.",
            }

        return {
            "success": True,
            "text": full_text,
            "page_count": 1,
            "word_count": word_count,
            "file_type": "DOCX",
            "is_scanned": False,
            "error": None,
            "suggestion": None,
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "word_count": 0,
            "file_type": "DOCX",
            "is_scanned": False,
            "error": f"Failed to parse DOCX: {str(e)}",
            "suggestion": "Ensure the document is a standard .docx file and not corrupted.",
        }


def parse_resume(file_source: Any, filename: str = "") -> Dict[str, Any]:
    """
    Universal parser for uploaded resumes. Detects file type from filename or header.

    Args:
        file_source: File path, BytesIO, or uploaded file object.
        filename: Optional filename hint to determine extension.

    Returns:
        Dict containing extraction result with status, text, metadata, and error handling.
    """
    if not filename and hasattr(file_source, "name"):
        filename = file_source.name

    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        return extract_from_pdf(file_source)
    elif filename_lower.endswith(".docx"):
        return extract_from_docx(file_source)
    elif filename_lower.endswith(".doc"):
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "word_count": 0,
            "file_type": "DOC",
            "is_scanned": False,
            "error": "Legacy .doc format is not supported directly.",
            "suggestion": "Please re-save or convert your file as .docx or .pdf in Word or Google Docs.",
        }
    elif filename_lower.endswith(".txt"):
        try:
            if isinstance(file_source, bytes):
                text = file_source.decode("utf-8", errors="ignore")
            elif isinstance(file_source, io.BytesIO):
                text = file_source.getvalue().decode("utf-8", errors="ignore")
            elif hasattr(file_source, "read"):
                content = file_source.read()
                if isinstance(content, bytes):
                    text = content.decode("utf-8", errors="ignore")
                else:
                    text = str(content)
            elif isinstance(file_source, str) and os.path.exists(file_source):
                with open(file_source, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            else:
                text = str(file_source)

            text = text.strip()
            word_count = len(text.split())
            if word_count < 3:
                return {
                    "success": False,
                    "text": "",
                    "page_count": 1,
                    "word_count": 0,
                    "file_type": "TXT",
                    "is_scanned": False,
                    "error": "The text file is empty.",
                    "suggestion": "Please paste or upload a resume with text content.",
                }

            return {
                "success": True,
                "text": text,
                "page_count": 1,
                "word_count": word_count,
                "file_type": "TXT",
                "is_scanned": False,
                "error": None,
                "suggestion": None,
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "page_count": 0,
                "word_count": 0,
                "file_type": "TXT",
                "is_scanned": False,
                "error": f"Failed reading text file: {e}",
                "suggestion": "Ensure the text file is UTF-8 encoded.",
            }
    else:
        # Default try PDF first, then DOCX
        pdf_res = extract_from_pdf(file_source)
        if pdf_res["success"]:
            return pdf_res
        if hasattr(file_source, "seek"):
            file_source.seek(0)
        docx_res = extract_from_docx(file_source)
        if docx_res["success"]:
            return docx_res
        return {
            "success": False,
            "text": "",
            "page_count": 0,
            "word_count": 0,
            "file_type": "UNKNOWN",
            "is_scanned": False,
            "error": "Unsupported file format.",
            "suggestion": "Please upload a .pdf, .docx, or .txt document.",
        }
