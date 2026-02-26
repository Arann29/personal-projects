from src.repositories.transactions import monthly_summary


def get_monthly_summary(month: str) -> dict:
    return monthly_summary(month)
