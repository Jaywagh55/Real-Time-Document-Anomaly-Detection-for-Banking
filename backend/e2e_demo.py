import requests
import time

API_JSON = "http://127.0.0.1:8000/api/v1/analyze"
API_FILES = "http://127.0.0.1:8000/api/v1/analyze_files"

PAYLOAD = {
    "application_id": "demo-001",
    "customer_id": "demo-cust",
    "documents": [
        {"id": "doc-1", "type": "financial_statement", "filename": "pnl.pdf", "content": "Total revenue: ₹1,20,00,000. Net profit: ₹32,00,000. GSTIN: 27ABCDE1234F1Z5."},
        {"id": "doc-2", "type": "land_record", "filename": "enc.pdf", "content": "Customer name: Rajesh Kumar. Survey no: 12567. Area: 3500 sqft."},
    ]
}

print("Running JSON demo")
resp = requests.post(API_JSON, json=PAYLOAD)
print(resp.status_code)
print(resp.json())

print("Running file upload demo (will POST a small sample if available)")
try:
    files = {"files": ("sample.txt", "Customer name: Demo. Survey no: 9999.")}
    data = {"application_id": "demo-001", "customer_id": "demo-cust"}
    r = requests.post(API_FILES, files=files, data=data)
    print(r.status_code)
    print(r.json())
except Exception as e:
    print("File upload demo failed:", e)
