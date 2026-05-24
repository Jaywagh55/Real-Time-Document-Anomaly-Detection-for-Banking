import re


def _regex_extract_entities(text: str) -> dict:
    if not text:
        return {
            "names": [],
            "parties": [],
            "dates": [],
            "amounts": [],
            "survey_numbers": [],
            "identifiers": [],
            "legal_terms": [],
        }

    text = text.strip()
    names = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)
    parties = []
    for pattern in [
        r"\b(?:issued by|seller|buyer|applicant|owner|beneficiary)[:\s]*([A-Z][A-Za-z\s]+?)\b(?=\.|,|\n|$)",
        r"\b(?:party|customer)[:\s]*([A-Z][A-Za-z\s]+?)\b(?=\.|,|\n|$)",
    ]:
        parties += re.findall(pattern, text, re.IGNORECASE)

    dates = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text)
    amounts = re.findall(r"₹\s?[\d,]+(?:\.\d+)?", text)
    survey_numbers = re.findall(
        r"\b(?:survey(?:\s*(?:no|number))?|s\.?no\.?|survey[- ]?no)[:\s]*([0-9A-Za-z\-/]+)\b",
        text,
        re.IGNORECASE,
    )
    identifiers = re.findall(r"\b(?:PAN|GSTIN|Aadhaar)[:\s]*([A-Z0-9\-]+)\b", text, re.IGNORECASE)
    legal_terms = re.findall(
        r"\b(encumbrance|mortgage|forgery|altered|copy|tender|agreement|title deed|NOC|stamp duty)\b",
        text,
        re.IGNORECASE,
    )

    normalized_ids = [m.upper() for m in identifiers]
    cleaned_parties = [p.strip() for p in parties if len(p.strip()) > 3]

    return {
        "names": list(dict.fromkeys(names)),
        "parties": list(dict.fromkeys(cleaned_parties)),
        "dates": list(dict.fromkeys(dates)),
        "amounts": list(dict.fromkeys(amounts)),
        "survey_numbers": list(dict.fromkeys(survey_numbers)),
        "identifiers": normalized_ids,
        "legal_terms": [term.lower() for term in dict.fromkeys(legal_terms)],
    }


def extract_entities(text: str) -> dict:
    """Extract structured entities. Prefer spaCy if available, otherwise use regex heuristics."""
    if not text:
        return _regex_extract_entities(text)

    try:
        import spacy

        # Try to load a small English model if available
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = spacy.blank("en")

        doc = nlp(text)
        names = [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG")]
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        amounts = [ent.text for ent in doc.ents if ent.label_ in ("MONEY", "QUANTITY")]
        identifiers = [ent.text for ent in doc.ents if ent.label_ in ("CARDINAL", "PRODUCT")]  # best-effort

        # Combine with regex to get survey numbers and legal terms
        extras = _regex_extract_entities(text)

        return {
            "names": list(dict.fromkeys(names)) or extras.get("names", []),
            "parties": extras.get("parties", []),
            "dates": list(dict.fromkeys(dates)) or extras.get("dates", []),
            "amounts": list(dict.fromkeys(amounts)) or extras.get("amounts", []),
            "survey_numbers": extras.get("survey_numbers", []),
            "identifiers": list(dict.fromkeys([s.upper() for s in identifiers])) or extras.get("identifiers", []),
            "legal_terms": extras.get("legal_terms", []),
        }
    except Exception:
        return _regex_extract_entities(text)
