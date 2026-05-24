# DocuShield

DocuShield is a real-time document anomaly detection platform for banking and finance underwriting. This repository contains a Python FastAPI backend and a simple React frontend prototype for document verification and risk scoring.

## Project Structure

- `backend/` — FastAPI backend, AI pipeline stub services, and API endpoints.
- `frontend/` — React prototype for submitting document bundles and showing risk summaries.

## Getting Started

### Backend

1. Navigate to `backend/`
2. Create a Python virtual environment.
3. Install dependencies from `requirements.txt`
4. Start the API with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend

1. Navigate to `frontend/`
2. Install dependencies with `npm install`
3. Start the development server with `npm run dev`

### Docker Compose

From the repository root, run:

```bash
docker compose up --build
```

This will start the backend on port `8000` and the frontend on port `5173`.

### One-Command Startup (Windows)

Run the PowerShell helper from the repository root:

```powershell
.\run.ps1
```

### Demo Data

A sample document bundle is available at `backend/sample_documents.json`.
Run the demo script after starting the backend:

```bash
cd backend
python demo_request.py
```

## Notes

- The current backend implementation contains stubbed AI/ML logic for proof of concept.
- The frontend communicates with the backend and displays a mock risk report.
- Extend the services under `backend/app/services/` to integrate OCR, forensics, NER, knowledge graph, and scoring logic.
