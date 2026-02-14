# data-pipeline-ml

Simple ETL + ML portfolio project with Docker.

## What it does

- Ingests CSV data
- Applies ETL cleaning and feature engineering
- Trains a regression model
- Serves predictions via API
- Checks data drift against training baseline
- Shows results in Streamlit dashboard

## Stack

- Python, FastAPI, pandas, scikit-learn
- PostgreSQL
- Streamlit
- Docker + Docker Compose

## Required CSV schema

`feature_1,feature_2,feature_3,target`

## Run

1. From `data-pipeline-ml/`:

```bash
docker compose up --build
```

1. Open:

- API docs: `http://localhost:8001/docs`
- Dashboard: `http://localhost:8502`

## Workflow demo

1. Upload `sample_data/train_sample.csv` in **Train model**
1. Run prediction with sample JSON in dashboard
1. Upload `sample_data/drift_sample.csv` in **Drift check**

## API endpoints

- `POST /ingest` — validate and transform a dataset
- `POST /train` — train model and store baseline stats
- `POST /predict` — return predictions for JSON records
- `POST /drift` — compare incoming data to baseline
- `GET /health` — health check

## Tests

```bash
pytest -q
```
