import pandas as pd


FEATURE_COLUMNS = ["feature_1", "feature_2", "feature_3"]
TARGET_COLUMN = "target"


def transform_dataframe(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    transformed = dataframe.copy()

    for column in FEATURE_COLUMNS + [TARGET_COLUMN]:
        transformed[column] = pd.to_numeric(transformed[column], errors="coerce")

    dropped_before_fill = int(transformed[FEATURE_COLUMNS].isna().any(axis=1).sum())

    for column in FEATURE_COLUMNS:
        transformed[column] = transformed[column].fillna(transformed[column].median())

    transformed[TARGET_COLUMN] = transformed[TARGET_COLUMN].fillna(transformed[TARGET_COLUMN].median())

    transformed["feature_ratio"] = transformed["feature_1"] / transformed["feature_2"].replace(0, 1)
    transformed["feature_interaction"] = transformed["feature_1"] * transformed["feature_3"]

    transformed = transformed.dropna()

    return transformed, dropped_before_fill
