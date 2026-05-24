from app.schemas import Document
import re


def extract_text_from_document(document: Document) -> str:
    """Extract text from a document payload, supporting direct content and OCR placeholder conversion."""
    if document.content:
        return document.content.strip()

    if document.filename:
        base = re.sub(r"\.[^.]+$", "", document.filename)
        base = re.sub(r"[_\-]+", " ", base).strip().title()
        return f"OCR extracted placeholder text for {base}. Document content is missing, so analysis uses available metadata."

    return "OCR extracted text placeholder"


def extract_text_from_bytes(content_bytes: bytes, filename: str = None) -> str:
    """Try to extract text from raw file bytes. Prefer pdfplumber for PDFs, otherwise fall back to pytesseract for images.

    This function is resilient: if pdfplumber or pytesseract are not installed it returns a useful placeholder.
    """
    import io

    # Try PDF first
    try:
        import pdfplumber

        if filename and filename.lower().endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
                text = "\n".join(pages).strip()
                if text:
                    return text
    except Exception:
        # pdfplumber not available or PDF parse failed; fallthrough
        pass

    # Try image OCR via pytesseract
    try:
        from PIL import Image
        import pytesseract

        img = Image.open(io.BytesIO(content_bytes)).convert("RGB")
        text = pytesseract.image_to_string(img)
        if text and text.strip():
            return text.strip()
    except Exception:
        pass

    # Fallback: return filename-based placeholder
    if filename:
        return f"[Unable to extract text — placeholder for {filename}]"

    return "[Unable to extract text from binary payload]"
