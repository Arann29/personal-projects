import json

from sqlalchemy import text

from src.db.database import get_session


def insert_receipt(image_path: str, extracted_payload: dict, transaction_id: int | None = None, confirmed: bool = False) -> int:
    with get_session() as session:
        row = session.execute(
            text(
                """
                INSERT INTO receipts (transaction_id, image_path, extracted_json, confirmed)
                VALUES (:transaction_id, :image_path, :extracted_json, :confirmed)
                RETURNING id
                """
            ),
            {
                "transaction_id": transaction_id,
                "image_path": image_path,
                "extracted_json": json.dumps(extracted_payload),
                "confirmed": 1 if confirmed else 0,
            },
        ).scalar_one()
    return int(row)


def attach_receipt_to_transaction(receipt_id: int, transaction_id: int) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                UPDATE receipts
                SET transaction_id = :transaction_id, confirmed = 1
                WHERE id = :receipt_id
                """
            ),
            {"transaction_id": transaction_id, "receipt_id": receipt_id},
        )
