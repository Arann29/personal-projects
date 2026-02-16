from io import StringIO

import pandas as pd

REQUIRED_COLUMNS = ["date", "ticker", "close", "shares"]


def extract_csv(file_bytes: bytes) -> pd.DataFrame:
    text = file_bytes.decode("utf-8")
    frame = pd.read_csv(StringIO(text))
    return frame


def transform_data(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    transformed = frame.copy()
    transformed["date"] = pd.to_datetime(transformed["date"], errors="coerce")
    transformed["ticker"] = transformed["ticker"].astype(str).str.upper().str.strip()
    transformed["close"] = pd.to_numeric(transformed["close"], errors="coerce")
    transformed["shares"] = pd.to_numeric(transformed["shares"], errors="coerce")

    transformed = transformed.dropna(subset=REQUIRED_COLUMNS)
    transformed = transformed[transformed["close"] > 0]
    transformed = transformed[transformed["shares"] >= 0]

    transformed = transformed.sort_values(["ticker", "date"]).reset_index(drop=True)
    transformed["market_value"] = transformed["close"] * transformed["shares"]

    if transformed.empty:
        raise ValueError("No valid rows after cleaning")

    return transformed
