
# Personal Finance Control Center

This project is now being upgraded from standalone scripts to a modular, extensible personal finance platform.

It keeps your original CSV/email workflow but adds a service architecture that supports:

- Manual cash transaction entry
- CSV import from old card exports
- Receipt ingestion flow (LLM vision + fallback parser)
- Rule-based categorization
- Monthly analytics by category
- FastAPI backend + Streamlit dashboard

## Current project layout

```text
project_manage_finance/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── db/
│   ├── repositories/
│   ├── ingestion/
│   ├── parsers/
│   ├── categorization/
│   ├── analytics/
│   └── models/
├── dashboard/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Legacy scripts

Your original scripts are still present and untouched:

- `manage_finances_m.py`
- `manage_finances_d.py`

These can still be used while you migrate to the new API-based flow.

## Quick start (local)

1. Create and activate an environment, then install dependencies:

```bash
pip install -r requirements.txt
```

1. Run the API:

```bash
uvicorn src.main:app --reload --port 8005
```

1. Run the dashboard:

```bash
streamlit run dashboard/app.py --server.port 8505
```

## Docker run

```bash
docker compose up --build
```

API: `http://localhost:8005/docs`

Dashboard: `http://localhost:8505`

## Implemented endpoints

- `GET /health`
- `POST /ingest/manual`
- `POST /ingest/csv`
- `POST /ingest/receipt`
- `POST /ingest/receipt/confirm`
- `GET /transactions`
- `GET /analytics/monthly/{month}`

## Receipt OCR fallback

`/ingest/receipt` now uses this chain:

1. LLM extraction (if `OPENAI_API_KEY` is set)
1. OCR fallback (`pytesseract` + image preprocessing)
1. Regex fallback from available text if OCR is not available

For local OCR, install the **Tesseract OCR engine** on your OS (Python package alone is not enough).

## Testing

```bash
pytest -q
```

## Next extension points

- Gmail ingestor strategy module to replace direct script runs
- Better OCR fallback for receipts
- Budget target APIs and recurring detection hooks
- Scheduled background ingestion (`scheduler/cron.py`)
