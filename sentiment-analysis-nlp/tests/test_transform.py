import pandas as pd

from src.etl.transform import transform_dataframe


def test_transform_dataframe_removes_short_rows():
    frame = pd.DataFrame(
        {
            "text": ["ok", "This is a valid review with enough content"],
            "date": ["2026-01-01", "2026-01-02"],
            "rating": [3, 5],
        }
    )

    transformed, dropped = transform_dataframe(frame)

    assert dropped == 1
    assert len(transformed) == 1
    assert "cleaned_text" in transformed.columns
