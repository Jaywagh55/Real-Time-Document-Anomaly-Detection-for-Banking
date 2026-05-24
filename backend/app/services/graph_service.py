from typing import List, Optional
import re
from app.schemas import Document
from app.services.neo4j_adapter import Neo4jAdapter


def _normalize_amount(amount_text: str) -> Optional[float]:
    if not amount_text:
        return None
    cleaned = re.sub(r"[^\d.]", "", amount_text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def link_entities(documents: List[Document]) -> dict:
    """Link entities across document bundle and identify cross-document matches and mismatches."""
    survey_index = {}
    identifier_index = {}
    party_index = {}
    linked_entities = []
    mismatches = []

    for doc in documents:
        entities = doc.entities or {}
        for survey in entities.get("survey_numbers", []):
            survey_index.setdefault(survey.lower(), []).append(doc)
        for identifier in entities.get("identifiers", []):
            identifier_index.setdefault(identifier.upper(), []).append(doc)
        for party in entities.get("parties", []):
            party_index.setdefault(party.lower(), []).append(doc)

    for entity_type, index in [
        ("survey_number", survey_index),
        ("identifier", identifier_index),
        ("party", party_index),
    ]:
        for value, docs in index.items():
            if len(docs) < 2:
                continue
            amount_values = [
                _normalize_amount(amount)
                for doc in docs
                for amount in (doc.entities or {}).get("amounts", [])
            ]
            amount_values = [value for value in amount_values if value is not None]
            owners = list({party for doc in docs for party in (doc.entities or {}).get("parties", [])})
            if entity_type == "survey_number" and len(set(amount_values)) > 1:
                mismatches.append({
                    "type": entity_type,
                    "value": value,
                    "documents": [doc.id for doc in docs],
                    "issue": "Inconsistent declared amount across same survey number entries.",
                    "confidence": 0.82,
                })
            linked_entities.append({
                "entity_type": entity_type,
                "value": value,
                "documents": [doc.id for doc in docs],
                "shared_amounts": [amt for amt in amount_values if amt is not None],
                "owners": owners,
                "confidence": 0.75 if len(docs) > 2 else 0.9,
            })

    for doc in documents:
        linked_entities.append({
            "document_id": doc.id,
            "entities": doc.entities or {},
            "shared_entity_count": sum(
                1 for index in (survey_index, identifier_index, party_index) for value in (doc.entities or {}).get("survey_numbers", []) if value.lower() in index and len(index[value.lower()]) > 1
            ),
            "confidence": 0.7,
        })

    result = {"linked_entities": linked_entities, "mismatches": mismatches}

    # Try to persist entities to Neo4j if adapter available (best-effort)
    try:
        adapter = Neo4jAdapter()
        if getattr(adapter, "available", False):
            # Flatten some entities into a simple list for ingestion
            to_write = []
            for doc in documents:
                ent = {
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "entities": doc.entities or {},
                }
                to_write.append(ent)
            write_result = adapter.write_entities(to_write)
            result["neo4j"] = write_result
        else:
            result["neo4j"] = {"status": "driver-not-available"}
    except Exception as e:
        result["neo4j"] = {"status": "error", "error": str(e)}

    return result
