from sqlalchemy import text

from src.db.database import get_session


def insert_documents(source_filename: str, rows: list[dict]) -> int:
    with get_session() as session:
        for row in rows:
            session.execute(
                text(
                    """
                    INSERT INTO documents (source_filename, review_date, rating, raw_text, cleaned_text)
                    VALUES (:source_filename, :review_date, :rating, :raw_text, :cleaned_text)
                    """
                ),
                {
                    "source_filename": source_filename,
                    "review_date": row.get("review_date"),
                    "rating": row.get("rating"),
                    "raw_text": row["raw_text"],
                    "cleaned_text": row["cleaned_text"],
                },
            )
    return len(rows)


def fetch_documents() -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT id, raw_text, cleaned_text, review_date, rating
                FROM documents
                ORDER BY id DESC
                """
            )
        ).mappings().all()
    return [dict(row) for row in rows]


def create_analysis_run(model_name: str, topic_count: int) -> int:
    with get_session() as session:
        run_id = session.execute(
            text(
                """
                INSERT INTO analysis_runs (model_name, topic_count)
                VALUES (:model_name, :topic_count)
                RETURNING id
                """
            ),
            {"model_name": model_name, "topic_count": topic_count},
        ).scalar_one()
    return int(run_id)


def save_analysis_results(run_id: int, rows: list[dict]) -> None:
    with get_session() as session:
        for row in rows:
            session.execute(
                text(
                    """
                    INSERT INTO analysis_results (run_id, document_id, sentiment_label, sentiment_score, topic_id, topic_keywords)
                    VALUES (:run_id, :document_id, :sentiment_label, :sentiment_score, :topic_id, :topic_keywords)
                    """
                ),
                {
                    "run_id": run_id,
                    "document_id": row["document_id"],
                    "sentiment_label": row["sentiment_label"],
                    "sentiment_score": row["sentiment_score"],
                    "topic_id": row["topic_id"],
                    "topic_keywords": row["topic_keywords"],
                },
            )


def latest_run_id() -> int | None:
    with get_session() as session:
        run_id = session.execute(
            text("SELECT id FROM analysis_runs ORDER BY id DESC LIMIT 1")
        ).scalar_one_or_none()
    return int(run_id) if run_id else None


def fetch_results(run_id: int) -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT ar.run_id, d.id AS document_id, d.raw_text, ar.sentiment_label, ar.sentiment_score, ar.topic_id, ar.topic_keywords
                FROM analysis_results ar
                JOIN documents d ON d.id = ar.document_id
                WHERE ar.run_id = :run_id
                ORDER BY ar.id DESC
                """
            ),
            {"run_id": run_id},
        ).mappings().all()
    return [dict(row) for row in rows]
