from app.schemas import DocumentBundle
from app.db import save_report

SEVERITY_SCORE = {
    "low": 6,
    "medium": 14,
    "high": 28,
}


def calculate_risk_report(bundle: DocumentBundle, registry_results: dict, cross_matches: dict) -> dict:
    """Generate a risk report using registry checks, forensics findings, and cross-document links."""
    findings = []
    score = 30.0

    for doc in bundle.documents:
        if doc.forensics and doc.forensics.get("issues"):
            for issue in doc.forensics["issues"]:
                severity = "high" if "forged" in issue["finding"].lower() or "inconsistent" in issue["finding"].lower() else "medium"
                findings.append({
                    "document_id": doc.id,
                    "issue": issue["finding"],
                    "severity": severity,
                    "evidence": issue.get("confidence") and f"Confidence {issue['confidence']:.0%} from forensic cues." or "Forensics heuristics flagged this item.",
                })
                score += SEVERITY_SCORE[severity]

    registry_status = registry_results.get("registry_status", {})
    if registry_status.get("ITR") == "mismatch":
        findings.append({
            "document_id": bundle.documents[0].id,
            "issue": "ITR registry mismatch detected",
            "severity": "high",
            "evidence": "Registry validation found inconsistent income disclosures in supporting documents.",
        })
        score += SEVERITY_SCORE["high"]

    if registry_status.get("GST") == "pending":
        findings.append({
            "document_id": bundle.documents[0].id,
            "issue": "GST registry status is pending",
            "severity": "medium",
            "evidence": "GST entry format or registration could not be fully verified.",
        })
        score += SEVERITY_SCORE["medium"]

    if registry_status.get("Bhulekh") == "pending":
        findings.append({
            "document_id": bundle.documents[0].id,
            "issue": "Bhulekh registry review required",
            "severity": "medium",
            "evidence": "Property encumbrance mention without an exact survey reference was detected.",
        })
        score += SEVERITY_SCORE["medium"]

    if cross_matches.get("mismatches"):
        for mismatch in cross_matches["mismatches"]:
            findings.append({
                "document_id": mismatch["documents"][0],
                "issue": mismatch["issue"],
                "severity": "high",
                "evidence": "Cross-document entity mismatch indicates conflicting records.",
            })
            score += SEVERITY_SCORE["high"]

    for link in cross_matches.get("linked_entities", []):
        if link.get("documents") and len(link["documents"]) > 1:
            findings.append({
                "document_id": link["documents"][0],
                "issue": f"Shared {link['entity_type']} across documents",
                "severity": "low",
                "evidence": "A common field was found in multiple documents, enabling stronger cross-checks.",
            })
            score += SEVERITY_SCORE["low"]

    score = min(score, 100.0)
    risk_level = "low"
    if score >= 70:
        risk_level = "high"
    elif score >= 45:
        risk_level = "medium"

    document_analysis = [
        {
            "id": doc.id,
            "type": doc.type,
            "filename": doc.filename,
            "text": doc.text,
            "entities": doc.entities or {},
            "forensics": doc.forensics or {},
        }
        for doc in bundle.documents
    ]
    # Build explainability (simple, synthetic attribution)
    try:
        forensics_count = sum(len((doc.forensics or {}).get("issues", [])) for doc in bundle.documents)
        forensics_score = min(30, forensics_count * 6)
    except Exception:
        forensics_score = 0

    registry_issues = 0
    try:
        rs = registry_results.get("registry_status", {})
        registry_issues = sum(1 for v in rs.values() if v in ("pending", "mismatch"))
    except Exception:
        registry_issues = 0
    registry_score = min(40, registry_issues * 12)

    crosslink_score = 0
    try:
        crosslink_score = len(cross_matches.get("mismatches", [])) * 20
    except Exception:
        crosslink_score = 0

    # Normalize into contributions (heuristic)
    raw = {
        "forensics": forensics_score,
        "registry": registry_score,
        "cross_links": crosslink_score,
        "base": 30,
    }
    total_raw = sum(raw.values()) or 1
    contributions = {k: round((v / total_raw) * 100, 1) for k, v in raw.items()}

    report = {
        "application_id": bundle.application_id,
        "customer_id": bundle.customer_id,
        "risk_score": round(score, 1),
        "risk_level": risk_level,
        "anomalies": findings,
        "registry_validation": registry_results,
        "cross_document_matches": cross_matches,
        "document_analysis": document_analysis,
        "explainability": {"raw": raw, "contributions_percent": contributions},
    }

    # best-effort persistence to audit DB
    try:
        save_report(bundle.application_id, bundle.customer_id, float(score), risk_level, report)
    except Exception:
        pass

    return report
