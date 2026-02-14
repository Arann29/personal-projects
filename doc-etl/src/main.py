from sqlalchemy import text
from fastapi import FastAPI, File, HTTPException, UploadFile

from src.db.database import get_session
from src.etl.extract import extract_text
from src.etl.load import insert_document, insert_extracted_record, insert_pipeline_error
from src.etl.transform import transform_text_to_record


app = FastAPI(title="doc-etl API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/process")
async def process_document(file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read()
        raw_text = extract_text(content, file.filename)
    except Exception as error:
        insert_pipeline_error(file.filename or "unknown", "extract", str(error))
        raise HTTPException(status_code=400, detail=f"Extraction failed: {error}")

    try:
        record = transform_text_to_record(raw_text)
    except Exception as error:
        insert_pipeline_error(file.filename or "unknown", "transform", str(error))
        raise HTTPException(status_code=500, detail=f"Transformation failed: {error}")

    try:
        document_id = insert_document(file.filename or "unknown", raw_text)
        insert_extracted_record(document_id, record)
        return {
            "id": document_id,
            "filename": file.filename,
            "status": "processed",
            "record": record.model_dump(mode="json"),
        }
    except Exception as error:
        insert_pipeline_error(file.filename or "unknown", "load", str(error))
        raise HTTPException(status_code=500, detail=f"Load failed: {error}")


@app.get("/documents")
def list_documents(limit: int = 20) -> dict:
    with get_session() as session:
        rows = session.execute(
            text(
                """
                SELECT id, filename, status, created_at
                FROM documents
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()

    return {"items": [dict(row) for row in rows]}


@app.get("/documents/{document_id}")
def get_document(document_id: int) -> dict:
    with get_session() as session:
        document = session.execute(
            text(
                """
                SELECT id, filename, raw_text, status, created_at
                FROM documents
                WHERE id = :document_id
                """
            ),
            {"document_id": document_id},
        ).mappings().first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        extracted = session.execute(
            text(
                """
                SELECT vendor_name, invoice_number, invoice_date, due_date,
                       currency, total_amount, tax_amount, category, notes
                FROM extracted_records
                WHERE document_id = :document_id
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"document_id": document_id},
        ).mappings().first()

    return {
        "id": document["id"],
        "filename": document["filename"],
        "status": document["status"],
        "created_at": str(document["created_at"]),
        "raw_text_preview": document["raw_text"][:1000],
        "extracted_data": dict(extracted) if extracted else {},
    }
