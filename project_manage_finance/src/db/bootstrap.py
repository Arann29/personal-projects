from pathlib import Path

from sqlalchemy import text

from src.db.database import engine


def initialize_database() -> None:
    sql_path = Path(__file__).parent / "init.sql"
    sql_content = sql_path.read_text(encoding="utf-8")

    statements = [statement.strip() for statement in sql_content.split(";") if statement.strip()]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
