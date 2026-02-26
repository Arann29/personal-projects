from sqlalchemy import text

from src.config import settings
from src.db.database import get_session


DEFAULT_ACCOUNTS = [
    ("Mastercard Pacificard", "credit_card"),
    ("Diners Club", "credit_card"),
    ("Cash", "cash"),
]


def seed_accounts() -> None:
    with get_session() as session:
        for name, account_type in DEFAULT_ACCOUNTS:
            session.execute(
                text(
                    """
                    INSERT OR IGNORE INTO accounts (name, type, currency)
                    VALUES (:name, :type, :currency)
                    """
                ),
                {"name": name, "type": account_type, "currency": settings.default_currency},
            )


def get_account_id(name: str) -> int:
    with get_session() as session:
        row = session.execute(
            text("SELECT id FROM accounts WHERE name = :name"),
            {"name": name},
        ).scalar_one_or_none()

        if row is not None:
            return int(row)

        session.execute(
            text(
                """
                INSERT INTO accounts (name, type, currency)
                VALUES (:name, 'cash', :currency)
                """
            ),
            {"name": name, "currency": settings.default_currency},
        )

    with get_session() as session:
        row = session.execute(
            text("SELECT id FROM accounts WHERE name = :name"),
            {"name": name},
        ).scalar_one()
    return int(row)
