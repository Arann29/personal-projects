import json

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from src.etl.extract import extract_csv
from src.etl.load import (
    load_baseline_stats,
    log_dataset,
    log_error,
    log_prediction,
    save_baseline_stats,
)
from src.etl.transform import transform_dataframe
from src.ml.monitor import baseline_stats, check_drift
from src.ml.predict import predict_records
from src.ml.train import train_model
from src.models.schemas import DriftResponse, IngestResponse, PredictRequest, PredictResponse, TrainResponse


app = FastAPI(title="data-pipeline-ml API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        payload = await file.read()
        frame = extract_csv(payload)
        transformed, dropped_rows = transform_dataframe(frame)
        log_dataset(file.filename or "uploaded.csv", len(transformed))
        return IngestResponse(
            rows_loaded=int(len(transformed)),
            rows_dropped=int(dropped_rows),
            columns=list(transformed.columns),
        )
    except Exception as error:
        log_error("ingest", str(error))
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/train", response_model=TrainResponse)
async def train(file: UploadFile = File(...)):
    try:
        payload = await file.read()
        frame = extract_csv(payload)
        transformed, _ = transform_dataframe(frame)

        rows_used, features = train_model(transformed)
        stats = baseline_stats(transformed)
        save_baseline_stats(stats)

        return TrainResponse(status="model_trained", rows_used=rows_used, features=features)
    except Exception as error:
        log_error("train", str(error))
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    try:
        predictions = predict_records(request.records)
        for payload, value in zip(request.records, predictions):
            log_prediction(payload, value)
        return PredictResponse(predictions=predictions)
    except Exception as error:
        log_error("predict", str(error))
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/drift", response_model=DriftResponse)
async def drift(file: UploadFile = File(...)):
    try:
        payload = await file.read()
        frame = extract_csv(payload)
        transformed, _ = transform_dataframe(frame)
        baseline = load_baseline_stats()
        drift_report = check_drift(transformed, baseline)
        return DriftResponse(**drift_report)
    except Exception as error:
        log_error("drift", str(error))
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/sample-payload")
def sample_payload() -> dict:
    rows = [
        {"feature_1": 10.0, "feature_2": 5.0, "feature_3": 2.0},
        {"feature_1": 4.5, "feature_2": 2.2, "feature_3": 1.3},
    ]
    return {"records": rows}
