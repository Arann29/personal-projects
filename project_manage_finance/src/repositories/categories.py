from sqlalchemy import text

from src.db.database import get_session


DEFAULT_CATEGORIES = [
    "Groceries",
    "Dining",
    "Transport",
    "Utilities",
    "Subscriptions",
    "Shopping",
    "Health",
    "Other",
]


def seed_categories() -> None:
    with get_session() as session:
        for name in DEFAULT_CATEGORIES:
            session.execute(
                text("INSERT OR IGNORE INTO categories (name) VALUES (:name)"),
                {"name": name},
            )


def get_category_id_by_name(name: str) -> int | None:
    with get_session() as session:
        row = session.execute(
            text("SELECT id FROM categories WHERE lower(name) = lower(:name)"),
            {"name": name},
        ).scalar_one_or_none()
    return int(row) if row is not None else None


def get_category_name_by_id(category_id: int | None) -> str | None:
    if category_id is None:
        return None
    with get_session() as session:
        row = session.execute(
            text("SELECT name FROM categories WHERE id = :category_id"),
            {"category_id": category_id},
        ).scalar_one_or_none()
    return str(row) if row is not None else None
