import os
from pathlib import Path

from fastapi.testclient import TestClient


DB_PATH = Path("test_finance.db")
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH.as_posix()}"

from src.main import app


def setup_module(module):
    if DB_PATH.exists():
        DB_PATH.unlink()


def test_manual_ingest_and_monthly_summary():
    with TestClient(app) as client:
        ingest_response = client.post(
            "/ingest/manual",
            json={
                "amount": 12.5,
                "description": "Coffee and snack",
                "merchant": "Local cafe",
                "account_name": "Cash",
            },
        )
        assert ingest_response.status_code == 200
        assert "transaction_id" in ingest_response.json()

        summary_response = client.get("/analytics/monthly/2026-02")
        assert summary_response.status_code == 200
        payload = summary_response.json()
        assert payload["month"] == "2026-02"
        assert payload["total_spent"] >= 12.5
