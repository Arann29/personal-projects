from io import BytesIO

import pandas as pd


REQUIRED_TEXT_COLUMNS = ["text", "review", "comment", "content"]


def extract_csv(payload: bytes) -> pd.DataFrame:
    dataframe = pd.read_csv(BytesIO(payload))
    if dataframe.empty:
        raise ValueError("Uploaded CSV is empty")
    return dataframe


def detect_text_column(columns: list[str]) -> str:
    normalized = {column.lower().strip(): column for column in columns}
    for candidate in REQUIRED_TEXT_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]
    raise ValueError("CSV must include one text column: text, review, comment, or content")
