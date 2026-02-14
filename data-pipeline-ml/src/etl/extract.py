from io import BytesIO

import pandas as pd


REQUIRED_COLUMNS = {"feature_1", "feature_2", "feature_3", "target"}


def extract_csv(file_bytes: bytes) -> pd.DataFrame:
    dataframe = pd.read_csv(BytesIO(file_bytes))
    missing = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_columns}")
    return dataframe
