import pandas as pd

from src.etl.transform import transform_dataframe


def test_transform_creates_engineered_features():
    frame = pd.DataFrame(
        [
            {"feature_1": 10, "feature_2": 5, "feature_3": 2, "target": 100},
            {"feature_1": 6, "feature_2": 3, "feature_3": 1, "target": 70},
        ]
    )

    transformed, dropped = transform_dataframe(frame)

    assert "feature_ratio" in transformed.columns
    assert "feature_interaction" in transformed.columns
    assert dropped == 0
