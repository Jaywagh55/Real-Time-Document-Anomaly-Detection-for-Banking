import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "docushield.db"


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id TEXT,
            customer_id TEXT,
            risk_score REAL,
            risk_level TEXT,
            report_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.commit()
    con.close()


def save_report(application_id: str, customer_id: str, risk_score: float, risk_level: str, report: dict):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO reports (application_id, customer_id, risk_score, risk_level, report_json) VALUES (?, ?, ?, ?, ?)",
        (application_id, customer_id, risk_score, risk_level, json.dumps(report)),
    )
    con.commit()
    con.close()


# Initialize DB on import (idempotent)
try:
    init_db()
except Exception:
    pass
