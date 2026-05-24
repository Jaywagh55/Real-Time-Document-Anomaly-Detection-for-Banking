from app.schemas import Document
import re


def run_pixel_forensics(document: Document) -> dict:
    """Detect suspicious artifacts in document content using heuristic rules."""
    issues = []
    text = (document.text or "").lower()

    if re.search(r"\b(₹|rs\.?|rupees?)\b", text) and re.search(r"\d{2,3},\d{2,3},\d{2,3}", text):
        issues.append({
            "type": "pixel_forensics",
            "finding": "High-value financial fields are present and may be forged.",
            "confidence": 0.82,
        })

    if re.search(r"\b(clone|copy|altered|forged|tamper)\b", text):
        issues.append({
            "type": "pixel_forensics",
            "finding": "Text indicates suspected document manipulation or forgery.",
            "confidence": 0.88,
        })

    suspicious_amounts = re.findall(r"₹\s?\d+[\d,]*", document.text or "")
    if len(suspicious_amounts) >= 2 and suspicious_amounts[0] != suspicious_amounts[-1]:
        issues.append({
            "type": "pixel_forensics",
            "finding": "Multiple inconsistent currency amounts were detected.",
            "confidence": 0.76,
        })

    if not issues:
        issues.append({
            "type": "pixel_forensics",
            "finding": "No obvious pixel-level anomalies were detected.",
            "confidence": 0.55,
        })

    return {"issues": issues}
