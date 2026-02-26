from datetime import date, datetime

from pydantic import BaseModel, Field


class ManualTransactionRequest(BaseModel):
    amount: float = Field(gt=0)
    description: str
    txn_datetime: datetime | None = None
    merchant: str | None = None
    account_name: str = "Cash"


class ReceiptExtractResponse(BaseModel):
    merchant: str | None = None
    txn_date: date | None = None
    total: float | None = None
    currency: str = "USD"
    items: list[dict] = Field(default_factory=list)
    raw_text: str | None = None
    extraction_method: str = "regex"
    confidence_score: float = 0.0
    confidence_by_field: dict[str, float] = Field(default_factory=dict)
    requires_review: bool = True


class ReceiptConfirmRequest(BaseModel):
    image_path: str
    merchant: str | None = None
    txn_date: date | None = None
    total: float = Field(gt=0)
    currency: str = "USD"
    description: str = "Receipt purchase"
    account_name: str = "Cash"


class TransactionOut(BaseModel):
    id: int
    txn_datetime: str
    amount: float
    currency: str
    description: str | None
    merchant: str | None
    category: str | None
    source: str


class MonthlySummaryOut(BaseModel):
    month: str
    total_spent: float
    by_category: dict[str, float]
