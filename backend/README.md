# DocuShield Backend

This backend uses FastAPI to host the document analysis API for the DocuShield project.

## Install

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

- `GET /health` — health check
- `POST /api/v1/analyze` — submit a document bundle for risk analysis

## Demo

A sample document bundle is included in `sample_documents.json`.
Start the backend and then run:

```bash
python demo_request.py
```

## One-Command Startup

On Windows, from the project root you can run:

```powershell
.\run.ps1
```

That command starts the backend and frontend together.
