import time
import requests
import json

API = "http://127.0.0.1:8000/api/v1/analyze"

PAYLOAD = {
    "application_id": "bench-001",
    "customer_id": "bench-cust",
    "documents": [
        {
            "id": "d1",
            "type": "financial_statement",
            "filename": "pnl.pdf",
            "content": "Total revenue: ₹1,20,00,000. Net profit: ₹32,00,000. GSTIN: 27ABCDE1234F1Z5. PAN: ABCDE1234F."
        },
        {
            "id": "d2",
            "type": "land_record",
            "filename": "enc.pdf",
            "content": "Customer name: Rajesh Kumar. Survey no: 12567. Area: 3500 sqft. Encumbrance date: 12-03-2026."
        }
    ]
}

RUNS = 10

latencies = []
for i in range(RUNS):
    t0 = time.time()
    r = requests.post(API, json=PAYLOAD)
    t1 = time.time()
    dt = t1 - t0
    latencies.append(dt)
    print(f"Run {i+1}: {dt:.3f}s - status {r.status_code}")

print("Average:", sum(latencies)/len(latencies))
print("Min:", min(latencies))
print("Max:", max(latencies))
