import json
import pathlib
import requests

BASE_URL = "http://localhost:8000/api/v1/analyze"


def load_sample_documents():
    sample_path = pathlib.Path(__file__).parent / "sample_documents.json"
    with sample_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_demo():
    payload = load_sample_documents()
    print("Sending sample document bundle to DocuShield API...\n")

    response = requests.post(BASE_URL, json=payload)
    response.raise_for_status()
    result = response.json()

    print("--- DocuShield Demo Result ---")
    print(f"Application ID: {result['application_id']}")
    print(f"Customer ID: {result['customer_id']}")
    print(f"Risk score: {result['risk_score']} ({result['risk_level']})")
    print("\nAnomalies:")
    for anomaly in result.get("anomalies", []):
        print(f"- [{anomaly['severity']}] {anomaly['issue']} | Evidence: {anomaly['evidence']}")
    print("\nRegistry validation:")
    print(json.dumps(result.get("registry_validation", {}), indent=2))
    print("\nCross-document matches:")
    print(json.dumps(result.get("cross_document_matches", {}), indent=2))


if __name__ == "__main__":
    run_demo()
