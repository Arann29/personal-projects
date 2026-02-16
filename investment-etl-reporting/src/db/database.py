import os

from sqlalchemy import create_engine


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5435/investment_reporting",
    )


engine = create_engine(get_database_url(), future=True)
