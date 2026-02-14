from sqlalchemy import text

from src.db.database import get_session
from src.models.schemas import ExtractedRecord


def insert_document(filename: str, raw_text: str, status: str = "processed") -> int:
    with get_session() as session:
        result = session.execute(
            text(
                """
                INSERT INTO documents (filename, raw_text, status)
                VALUES (:filename, :raw_text, :status)
                RETURNING id
                """
            ),
            {"filename": filename, "raw_text": raw_text, "status": status},
        )
        return int(result.scalar_one())


def insert_extracted_record(document_id: int, record: ExtractedRecord) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                INSERT INTO extracted_records (
                    document_id, vendor_name, invoice_number, invoice_date, due_date,
                    currency, total_amount, tax_amount, category, notes
                )
                VALUES (
                    :document_id, :vendor_name, :invoice_number, :invoice_date, :due_date,
                    :currency, :total_amount, :tax_amount, :category, :notes
                )
                """
            ),
            {
                "document_id": document_id,
                "vendor_name": record.vendor_name,
                "invoice_number": record.invoice_number,
                "invoice_date": record.invoice_date,
                "due_date": record.due_date,
                "currency": record.currency,
                "total_amount": record.total_amount,
                "tax_amount": record.tax_amount,
                "category": record.category,
                "notes": record.notes,
            },
        )


def insert_pipeline_error(filename: str, stage: str, error_message: str) -> None:
    with get_session() as session:
        session.execute(
            text(
                """
                INSERT INTO pipeline_errors (filename, stage, error_message)
                VALUES (:filename, :stage, :error_message)
                """
            ),
            {"filename": filename, "stage": stage, "error_message": error_message[:2000]},
        )
