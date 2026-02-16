import pandas as pd

from src.services.metrics import calculate_metrics


def test_calculate_metrics_returns_expected_columns():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-03",
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-03",
                ]
            ),
            "ticker": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "close": [100, 102, 101, 50, 52, 53],
            "shares": [10, 10, 10, 20, 20, 20],
            "market_value": [1000, 1020, 1010, 1000, 1040, 1060],
        }
    )

    metrics = calculate_metrics(frame)

    expected_cols = {
        "ticker",
        "avg_daily_return",
        "volatility",
        "total_return",
        "max_drawdown",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
    }
    assert expected_cols.issubset(set(metrics.columns))
    assert len(metrics) == 2


def test_total_return_is_computed():
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
            "ticker": ["AAA", "AAA", "AAA"],
            "close": [100, 110, 120],
            "shares": [1, 1, 1],
            "market_value": [100, 110, 120],
        }
    )

    metrics = calculate_metrics(frame)
    total_return = float(metrics.iloc[0]["total_return"])

    assert round(total_return, 4) == 0.2
