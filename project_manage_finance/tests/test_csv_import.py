from src.ingestion.csv_import import import_csv_transactions
from src.db.bootstrap import initialize_database
from src.repositories.accounts import seed_accounts
from src.repositories.categories import seed_categories


def test_import_csv_transactions_runs():
    initialize_database()
    seed_accounts()
    seed_categories()
    inserted = import_csv_transactions("transactions_December_2024_master.csv", "Mastercard Pacificard")
    assert inserted >= 1
