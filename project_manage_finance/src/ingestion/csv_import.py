import csv
import datetime
from pathlib import Path

from src.categorization.pipeline import classify_transaction
from src.repositories.accounts import get_account_id
from src.repositories.categories import get_category_id_by_name
from src.repositories.transactions import insert_transaction


def import_csv_transactions(file_path: str, account_name: str, currency: str = "USD") -> int:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    account_id = get_account_id(account_name)
    inserted = 0

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            date_value = row.get("Date") or row.get("date")
            amount_value = row.get("Amount") or row.get("amount")

            if not date_value or not amount_value:
                continue

            txn_datetime = datetime.datetime.strptime(date_value.strip(), "%Y-%m-%d %H:%M")
            amount = float(str(amount_value).strip())
            description = f"Imported from {path.name}"
            category_name = classify_transaction(description)
            category_id = get_category_id_by_name(category_name)

            insert_transaction(
                account_id=account_id,
                txn_datetime=txn_datetime,
                amount=amount,
                currency=currency,
                description=description,
                merchant=None,
                category_id=category_id,
                source="csv_import",
            )
            inserted += 1

    return inserted
