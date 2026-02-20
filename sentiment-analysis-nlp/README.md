# sentiment-analysis-nlp

Sentiment and topic analysis project using FastAPI, Streamlit, and PostgreSQL.

## What it does

- Ingests review text data from CSV
- Cleans and validates text fields
- Runs transformer-based sentiment analysis
- Builds topic clusters using TF-IDF + KMeans
- Stores analysis runs and per-document outputs in PostgreSQL
- Generates concise analysis summaries (LLM if API key is present, fallback otherwise)
- Shows results in a Streamlit dashboard

## Stack

- Python, FastAPI, pandas, scikit-learn, transformers
- PostgreSQL
- Streamlit
- Docker + Docker Compose

## Required CSV schema

At least one text column from:

`text` or `review` or `comment` or `content`

Optional columns:

`date`, `rating`

## Run

1. From `sentiment-analysis-nlp/`:

```bash
docker compose up --build
```

1. Open:

- API docs: `http://localhost:8003/docs`
- Dashboard: `http://localhost:8504`

## Workflow demo

1. Upload `sample_data/reviews.csv` in **Ingest dataset**
2. Click **Run analysis**
3. Click **Load latest results**
4. Inspect sentiment bars, topic bars, and summary output

## API endpoints

- `POST /ingest` — upload CSV and store cleaned text rows
- `POST /analyze` — run sentiment + topic analysis and store outputs
- `GET /results` — return latest run records (or selected run)
- `GET /summary` — return summary text for latest run
- `GET /health` — health check

## Tests

```bash
pytest -q
```
