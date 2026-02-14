from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExtractedRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    currency: Optional[str] = Field(default=None, max_length=5)
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class ProcessResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str


class DocumentSummary(BaseModel):
    id: int
    filename: str
    status: str
    created_at: str


class DocumentDetail(BaseModel):
    id: int
    filename: str
    status: str
    raw_text_preview: str
    created_at: str
    extracted_data: dict
