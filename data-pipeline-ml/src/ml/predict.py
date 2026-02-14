import joblib
import pandas as pd

from src.config import settings
from src.ml.train import MODEL_FEATURES


def _prepare_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()
    for column in ["feature_1", "feature_2", "feature_3"]:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    data["feature_ratio"] = data["feature_1"] / data["feature_2"].replace(0, 1)
    data["feature_interaction"] = data["feature_1"] * data["feature_3"]

    return data[MODEL_FEATURES]


def predict_records(records: list[dict]) -> list[float]:
    model = joblib.load(settings.model_path)
    frame = pd.DataFrame(records)
    features = _prepare_features(frame)
    predictions = model.predict(features)
    return [float(item) for item in predictions]
