from datetime import datetime

from src.categorization.pipeline import classify_transaction
from src.repositories.accounts import get_account_id
from src.repositories.categories import get_category_id_by_name
from src.repositories.transactions import insert_transaction


def ingest_manual_transaction(
    amount: float,
    description: str,
    txn_datetime: datetime | None = None,
    merchant: str | None = None,
    account_name: str = "Cash",
    currency: str = "USD",
) -> int:
    effective_datetime = txn_datetime or datetime.now()
    category_name = classify_transaction(description, merchant)
    category_id = get_category_id_by_name(category_name)
    account_id = get_account_id(account_name)

    return insert_transaction(
        account_id=account_id,
        txn_datetime=effective_datetime,
        amount=amount,
        currency=currency,
        description=description,
        merchant=merchant,
        category_id=category_id,
        source="manual",
    )
