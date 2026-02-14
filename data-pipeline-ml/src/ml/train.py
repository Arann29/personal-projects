import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.config import settings
from src.etl.transform import FEATURE_COLUMNS


MODEL_FEATURES = FEATURE_COLUMNS + ["feature_ratio", "feature_interaction"]


def train_model(dataframe: pd.DataFrame) -> tuple[int, list[str]]:
    model = RandomForestRegressor(n_estimators=120, random_state=42)

    x_train = dataframe[MODEL_FEATURES]
    y_train = dataframe["target"]
    model.fit(x_train, y_train)

    os.makedirs(os.path.dirname(settings.model_path), exist_ok=True)
    joblib.dump(model, settings.model_path)

    return len(dataframe), MODEL_FEATURES
