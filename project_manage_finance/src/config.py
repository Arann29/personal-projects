import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///finance.db")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    default_currency: str = os.getenv("DEFAULT_CURRENCY", "USD")


settings = Settings()
