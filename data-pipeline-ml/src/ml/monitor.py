import pandas as pd

from src.etl.transform import FEATURE_COLUMNS


def baseline_stats(dataframe: pd.DataFrame) -> list[dict]:
    rows = []
    for column in FEATURE_COLUMNS:
        series = pd.to_numeric(dataframe[column], errors="coerce")
        rows.append(
            {
                "feature_name": column,
                "mean_value": float(series.mean()),
                "std_value": float(series.std(ddof=0)) if series.std(ddof=0) is not None else 0.0,
                "missing_rate": float(series.isna().mean()),
            }
        )
    return rows


def check_drift(dataframe: pd.DataFrame, baseline: list[dict]) -> dict:
    details = {}
    drift_flags = []

    baseline_by_name = {row["feature_name"]: row for row in baseline}

    for column in FEATURE_COLUMNS:
        current = pd.to_numeric(dataframe[column], errors="coerce")
        current_mean = float(current.mean())
        current_missing = float(current.isna().mean())

        base = baseline_by_name.get(column)
        if not base:
            details[column] = {"status": "no_baseline"}
            drift_flags.append(True)
            continue

        base_mean = base["mean_value"]
        base_missing = base["missing_rate"]
        mean_delta = abs(current_mean - base_mean)
        missing_delta = abs(current_missing - base_missing)

        mean_threshold = max(abs(base_mean) * 0.20, 0.5)
        missing_threshold = 0.10

        drift = mean_delta > mean_threshold or missing_delta > missing_threshold
        drift_flags.append(drift)

        details[column] = {
            "drift": drift,
            "base_mean": base_mean,
            "current_mean": current_mean,
            "base_missing_rate": base_missing,
            "current_missing_rate": current_missing,
            "mean_threshold": mean_threshold,
            "missing_threshold": missing_threshold,
        }

    return {"drift_detected": any(drift_flags), "details": details}
