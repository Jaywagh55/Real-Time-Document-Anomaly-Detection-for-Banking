from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from app.schemas import DocumentBundle, RiskReport, Document
from app.services.ocr_service import extract_text_from_document, extract_text_from_bytes
from app.services.forensics_service import run_pixel_forensics
from app.services.ela_service import compute_ela_bytes
from app.services.ner_service import extract_entities
from app.services.registry_adapter import default_registry_adapter
from app.services.graph_service import link_entities
from app.services.scoring_service import calculate_risk_report

import io

router = APIRouter()


@router.post("/analyze", response_model=RiskReport)
async def analyze_document_bundle(bundle: DocumentBundle):
    if not bundle.documents:
        raise HTTPException(status_code=400, detail="At least one document is required.")

    for doc in bundle.documents:
        doc.text = extract_text_from_document(doc)
        doc.forensics = run_pixel_forensics(doc)
        doc.entities = extract_entities(doc.text)

    registry_results = default_registry_adapter.validate_documents(bundle.documents)
    cross_matches = link_entities(bundle.documents)
    report = calculate_risk_report(bundle, registry_results, cross_matches)
    return report


@router.post("/analyze_files", response_model=RiskReport)
async def analyze_file_upload(
    files: List[UploadFile] = File(...),
    application_id: str = Form(...),
    customer_id: str = Form(...),
):
    """Accept multiple uploaded files (PDFs/images), extract text, and run the same pipeline as JSON analyze."""
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required.")

    documents: List[Document] = []
    for idx, up in enumerate(files):
        content = await up.read()
        text = extract_text_from_bytes(content, up.filename)
        doc = Document(id=f"file-{idx+1}", type="uploaded", filename=up.filename, content=None)
        doc.text = text
        # Run heuristic forensics and attach ELA when applicable
        doc.forensics = run_pixel_forensics(doc)
        try:
            ela = compute_ela_bytes(content, up.filename)
            doc.forensics = doc.forensics or {}
            doc.forensics["ela"] = ela
        except Exception:
            # don't fail the whole request if ELA fails
            doc.forensics = doc.forensics or {}
            doc.forensics["ela_error"] = "ELA processing not available"
        doc.entities = extract_entities(doc.text)
        documents.append(doc)

    bundle = DocumentBundle(application_id=application_id, customer_id=customer_id, documents=documents)
    registry_results = default_registry_adapter.validate_documents(bundle.documents)
    cross_matches = link_entities(bundle.documents)
    report = calculate_risk_report(bundle, registry_results, cross_matches)
    return report
