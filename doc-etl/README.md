# doc-etl

Simple, recruiter-friendly ETL portfolio project:

- Upload a document (`.txt` or `.pdf`)
- Extract key invoice fields (LLM if API key exists, fallback parser otherwise)
- Validate and normalize data with Pydantic
- Load clean records into PostgreSQL
- Review results in FastAPI and Streamlit

## Stack

- Python, FastAPI, Pydantic, SQLAlchemy
- PostgreSQL
- Streamlit
- Docker + Docker Compose

## Architecture

1. **Extract**: parse uploaded text/PDF
2. **Transform**: extract structured fields (`invoice_number`, `currency`, `total_amount`, etc.)
3. **Load**: store document, extracted record, and pipeline errors in PostgreSQL

## Run

1. From `doc-etl/`, ensure `.env` exists (already created)
1. Start services:

```bash
docker compose up --build
```

1. Open:

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8501`

## API Endpoints

- `POST /process` — upload a document file
- `GET /documents` — list recent processed documents
- `GET /documents/{id}` — get document detail and extracted data
- `GET /health` — health check

## Notes

- If `OPENAI_API_KEY` is present, the transform step uses LLM extraction.
- If no API key is set (or API fails), fallback regex extraction is used.
- PostgreSQL is exposed on host port `5433` to avoid conflicts.

## Test

```bash
pytest -q
```
