from sqlalchemy import text

from src.db.database import get_session


def log_dataset(source_name: str, row_count: int) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                INSERT INTO datasets (source_name, row_count)
                VALUES (:source_name, :row_count)
                """
            ),
            {"source_name": source_name, "row_count": row_count},
        )


def log_error(stage: str, error_message: str) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                INSERT INTO pipeline_errors (stage, error_message)
                VALUES (:stage, :error_message)
                """
            ),
            {"stage": stage, "error_message": error_message[:2000]},
        )


def save_baseline_stats(stats_rows: list[dict]) -> None:
    with get_session() as session:
        session.execute(text("DELETE FROM training_baseline"))
        for row in stats_rows:
            session.execute(
                text(
                    """
                    INSERT INTO training_baseline (feature_name, mean_value, std_value, missing_rate)
                    VALUES (:feature_name, :mean_value, :std_value, :missing_rate)
                    """
                ),
                row,
            )


def load_baseline_stats() -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT feature_name, mean_value, std_value, missing_rate
                FROM training_baseline
                """
            )
        ).mappings().all()
    return [dict(row) for row in rows]


def log_prediction(payload: dict, prediction: float) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                INSERT INTO predictions_log (payload, prediction)
                VALUES (:payload, :prediction)
                """
            ),
            {"payload": payload, "prediction": prediction},
        )
