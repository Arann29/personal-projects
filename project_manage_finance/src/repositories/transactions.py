from collections import defaultdict
from datetime import datetime

from sqlalchemy import text

from src.db.database import get_session


def insert_transaction(
    account_id: int,
    txn_datetime: datetime,
    amount: float,
    currency: str,
    description: str,
    merchant: str | None,
    category_id: int | None,
    source: str,
    notes: str | None = None,
) -> int:
    with get_session() as session:
        result = session.execute(
            text(
                """
                INSERT OR IGNORE INTO transactions
                (account_id, txn_datetime, amount, currency, description, merchant, category_id, source, notes)
                VALUES (:account_id, :txn_datetime, :amount, :currency, :description, :merchant, :category_id, :source, :notes)
                RETURNING id
                """
            ),
            {
                "account_id": account_id,
                "txn_datetime": txn_datetime.isoformat(),
                "amount": amount,
                "currency": currency,
                "description": description,
                "merchant": merchant,
                "category_id": category_id,
                "source": source,
                "notes": notes,
            },
        ).scalar_one_or_none()

        if result is not None:
            return int(result)

    with get_session() as session:
        existing = session.execute(
            text(
                """
                SELECT id FROM transactions
                WHERE account_id = :account_id AND txn_datetime = :txn_datetime
                  AND amount = :amount AND description = :description
                ORDER BY id DESC LIMIT 1
                """
            ),
            {
                "account_id": account_id,
                "txn_datetime": txn_datetime.isoformat(),
                "amount": amount,
                "description": description,
            },
        ).scalar_one()
    return int(existing)


def list_transactions(limit: int = 200) -> list[dict]:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT t.id, t.txn_datetime, t.amount, t.currency, t.description, t.merchant,
                       c.name as category_name, t.source
                FROM transactions t
                LEFT JOIN categories c ON c.id = t.category_id
                ORDER BY t.txn_datetime DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
    return [dict(row) for row in rows]


def monthly_summary(month: str) -> dict:
    with get_session() as session:
        total = session.execute(
            text(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE substr(txn_datetime, 1, 7) = :month
                """
            ),
            {"month": month},
        ).scalar_one()

        rows = session.execute(
            text(
                """
                SELECT COALESCE(c.name, 'Uncategorized') AS category_name,
                       COALESCE(SUM(t.amount), 0) AS category_total
                FROM transactions t
                LEFT JOIN categories c ON c.id = t.category_id
                WHERE substr(t.txn_datetime, 1, 7) = :month
                GROUP BY COALESCE(c.name, 'Uncategorized')
                ORDER BY category_total DESC
                """
            ),
            {"month": month},
        ).mappings().all()

    by_category = defaultdict(float)
    for row in rows:
        by_category[str(row["category_name"])] = float(row["category_total"])

    return {"month": month, "total_spent": float(total), "by_category": dict(by_category)}
