from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile

from src.analytics.monthly import get_monthly_summary
from src.db.bootstrap import initialize_database
from src.ingestion.csv_import import import_csv_transactions
from src.ingestion.manual import ingest_manual_transaction
from src.ingestion.receipt import extract_receipt
from src.models.schemas import (
    ManualTransactionRequest,
    MonthlySummaryOut,
    ReceiptConfirmRequest,
    ReceiptExtractResponse,
    TransactionOut,
)
from src.repositories.accounts import get_account_id, seed_accounts
from src.repositories.categories import get_category_id_by_name, get_category_name_by_id, seed_categories
from src.repositories.receipts import attach_receipt_to_transaction, insert_receipt
from src.repositories.transactions import insert_transaction, list_transactions


app = FastAPI(title="Personal Finance Control Center API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    initialize_database()
    seed_accounts()
    seed_categories()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest/manual")
def ingest_manual(request: ManualTransactionRequest) -> dict:
    transaction_id = ingest_manual_transaction(
        amount=request.amount,
        description=request.description,
        txn_datetime=request.txn_datetime,
        merchant=request.merchant,
        account_name=request.account_name,
    )
    return {"transaction_id": transaction_id}


@app.post("/ingest/csv")
def ingest_csv(file_path: str, account_name: str) -> dict:
    inserted = import_csv_transactions(file_path=file_path, account_name=account_name)
    return {"inserted": inserted}


@app.post("/ingest/receipt", response_model=ReceiptExtractResponse)
async def ingest_receipt(file: UploadFile = File(...)):
    receipts_dir = Path("receipts")
    receipts_dir.mkdir(exist_ok=True)

    suffix = Path(file.filename or "receipt.jpg").suffix or ".jpg"
    file_path = receipts_dir / f"{uuid4().hex}{suffix}"
    payload = await file.read()
    file_path.write_bytes(payload)

    extracted = extract_receipt(str(file_path))
    insert_receipt(str(file_path), extracted, confirmed=False)
    return ReceiptExtractResponse(**extracted)


@app.post("/ingest/receipt/confirm")
def confirm_receipt(request: ReceiptConfirmRequest) -> dict:
    txn_datetime = datetime.combine(request.txn_date or datetime.today().date(), datetime.min.time())
    category_id = get_category_id_by_name("Other")
    account_id = get_account_id(request.account_name)

    transaction_id = insert_transaction(
        account_id=account_id,
        txn_datetime=txn_datetime,
        amount=request.total,
        currency=request.currency,
        description=request.description,
        merchant=request.merchant,
        category_id=category_id,
        source="receipt",
    )

    receipt_id = insert_receipt(
        image_path=request.image_path,
        extracted_payload={
            "merchant": request.merchant,
            "txn_date": str(request.txn_date) if request.txn_date else None,
            "total": request.total,
            "currency": request.currency,
        },
        transaction_id=transaction_id,
        confirmed=True,
    )
    attach_receipt_to_transaction(receipt_id, transaction_id)

    return {"transaction_id": transaction_id, "receipt_id": receipt_id}


@app.get("/transactions", response_model=list[TransactionOut])
def transactions(limit: int = 200):
    rows = list_transactions(limit=limit)
    return [
        TransactionOut(
            id=row["id"],
            txn_datetime=row["txn_datetime"],
            amount=float(row["amount"]),
            currency=row["currency"],
            description=row["description"],
            merchant=row["merchant"],
            category=row.get("category_name"),
            source=row["source"],
        )
        for row in rows
    ]


@app.get("/analytics/monthly/{month}", response_model=MonthlySummaryOut)
def monthly(month: str):
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError as error:
        raise HTTPException(status_code=400, detail="month must be YYYY-MM") from error

    summary = get_monthly_summary(month)
    return MonthlySummaryOut(**summary)
