from typing import List, Dict
from app.schemas import Document


class RegistryAdapter:
    """Base class for registry adapters. Implementations should override `validate_documents`.

    The function returns a dict with `registry_status` and optional `validation_notes`.
    """

    def validate_documents(self, documents: List[Document]) -> Dict:
        raise NotImplementedError()


class MockRegistryAdapter(RegistryAdapter):
    """Mimics registry checks using heuristics (existing mock logic moved here)."""

    def validate_documents(self, documents: List[Document]) -> Dict:
        status = {
            "Bhulekh": "verified",
            "MCA21": "verified",
            "CERSAI": "verified",
            "GST": "verified",
            "ITR": "verified",
        }
        notes = []

        for doc in documents:
            text = (doc.text or "").lower()
            if "itr" in text or "income" in text:
                if "mismatch" in text or "declared income differs" in text:
                    status["ITR"] = "mismatch"
                    notes.append("Detected ITR-related content with inconsistent income disclosures.")
                else:
                    notes.append("ITR profile references found; registry check passes if formats are consistent.")

            if "gst" in text:
                if "27" not in text or ("gstin" in text and not any(part.isdigit() for part in text.split() if part.isdigit())):
                    status["GST"] = "pending"
                    notes.append("GST entry requires verification due to missing or unusual GSTIN format.")
                else:
                    notes.append("GST references were found and appear structurally valid.")

            if "encumbrance" in text:
                if "survey" not in text:
                    status["Bhulekh"] = "pending"
                    notes.append("Encumbrance remark is present without a clear survey reference; Bhulekh review recommended.")
                else:
                    notes.append("Encumbrance details appear in line with registry records.")

            if "forged" in text or "altered" in text or "copy" in text:
                status["CERSAI"] = "pending"
                notes.append("Document text contains indicators of potential forgery or alteration.")

        return {"registry_status": status, "validation_notes": notes}


# Export a default adapter instance (can be swapped by importers)
default_registry_adapter = MockRegistryAdapter()
