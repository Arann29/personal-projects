import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/pipelineml",
    )
    model_path: str = os.getenv("MODEL_PATH", "trained_model/model.pkl")


settings = Settings()
