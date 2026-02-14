from typing import Any

from pydantic import BaseModel


class IngestResponse(BaseModel):
    rows_loaded: int
    rows_dropped: int
    columns: list[str]


class TrainResponse(BaseModel):
    status: str
    rows_used: int
    features: list[str]


class PredictRequest(BaseModel):
    records: list[dict[str, Any]]


class PredictResponse(BaseModel):
    predictions: list[float]


class DriftResponse(BaseModel):
    drift_detected: bool
    details: dict[str, Any]
