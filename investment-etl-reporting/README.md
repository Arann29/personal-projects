# investment-etl-reporting

Simple finance-focused ETL + reporting project with Docker.

## What it does

- Ingests portfolio price CSV data (`date,ticker,close,shares`)
- Cleans and validates records
- Computes investment metrics per ticker
- Stores run history and metrics in PostgreSQL
- Generates a markdown investment performance report
- Shows workflow in a Streamlit dashboard

## Stack

- Python, FastAPI, pandas, SQLAlchemy
- PostgreSQL
- Streamlit
- Docker + Docker Compose

## Required CSV schema

`date,ticker,close,shares`

## Run

1. From `investment-etl-reporting/`:

```bash
docker compose up --build
```

1. Open:

- API docs: `http://localhost:8002/docs`
- Dashboard: `http://localhost:8503`

## Workflow demo

1. Upload `sample_data/portfolio_prices.csv` in **Run ingestion**
2. Click **Load summary** to view computed metrics
3. Click **Generate markdown report** and download the report

## API endpoints

- `POST /ingest` — validate CSV, compute metrics, store run + metrics
- `GET /metrics/summary` — return summary for latest or selected run
- `POST /report` — generate and store markdown report
- `GET /report/latest` — fetch latest generated report
- `GET /health` — health check

## Tests

```bash
pytest -q
```
