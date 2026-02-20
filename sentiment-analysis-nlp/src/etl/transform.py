import re

import pandas as pd

from src.etl.extract import detect_text_column


URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
SPACE_PATTERN = re.compile(r"\s+")


def clean_text(value: str) -> str:
    text = str(value)
    text = URL_PATTERN.sub("", text)
    text = text.replace("\n", " ").replace("\r", " ")
    text = SPACE_PATTERN.sub(" ", text).strip()
    return text


def transform_dataframe(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    text_column = detect_text_column(list(frame.columns))

    transformed = frame.copy()
    transformed["raw_text"] = transformed[text_column].astype(str)
    transformed["cleaned_text"] = transformed["raw_text"].map(clean_text)

    before_count = len(transformed)
    transformed = transformed[transformed["cleaned_text"].str.len() > 3].copy()
    dropped_rows = before_count - len(transformed)

    transformed["rating"] = pd.to_numeric(transformed.get("rating"), errors="coerce")
    transformed["review_date"] = pd.to_datetime(transformed.get("date"), errors="coerce").dt.date

    return transformed[["raw_text", "cleaned_text", "rating", "review_date"]], dropped_rows
