from typing import List, Optional
from pydantic import BaseModel


class Document(BaseModel):
    id: str
    type: str
    filename: Optional[str] = None
    content: Optional[str] = None
    text: Optional[str] = None
    forensics: Optional[dict] = None
    entities: Optional[dict] = None


class DocumentBundle(BaseModel):
    application_id: str
    customer_id: str
    documents: List[Document]


class AnomalyFinding(BaseModel):
    document_id: str
    issue: str
    severity: str
    evidence: str


class DocumentAnalysis(BaseModel):
    id: str
    type: str
    filename: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[dict] = None
    forensics: Optional[dict] = None


class RiskReport(BaseModel):
    application_id: str
    customer_id: str
    risk_score: float
    risk_level: str
    anomalies: List[AnomalyFinding]
    document_analysis: List[DocumentAnalysis]
    registry_validation: dict
    cross_document_matches: dict
