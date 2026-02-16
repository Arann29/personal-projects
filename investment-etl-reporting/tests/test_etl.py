import pandas as pd
import pytest

from src.services.etl import transform_data


def test_transform_data_validates_required_columns():
    frame = pd.DataFrame({"date": ["2026-01-01"], "ticker": ["AAA"]})

    with pytest.raises(ValueError):
        transform_data(frame)


def test_transform_data_cleans_and_adds_market_value():
    frame = pd.DataFrame(
        {
            "date": ["2026-01-01", "bad-date"],
            "ticker": ["aaa", "bbb"],
            "close": [100, -1],
            "shares": [2, 5],
        }
    )

    transformed = transform_data(frame)

    assert len(transformed) == 1
    assert transformed.iloc[0]["ticker"] == "AAA"
    assert float(transformed.iloc[0]["market_value"]) == 200
