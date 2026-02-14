import json
import re
from datetime import date
from decimal import Decimal
from io import BytesIO

from openai import OpenAI

from src.config import settings
from src.models.schemas import ExtractedRecord


CURRENCY_PATTERN = re.compile(r"\b(EUR|USD|GBP)\b", re.IGNORECASE)
AMOUNT_PATTERN = re.compile(r"(?:total|amount)\s*[:\-]?\s*([0-9]+(?:[\.,][0-9]{1,2})?)", re.IGNORECASE)
INVOICE_PATTERN = re.compile(r"(?:invoice\s*(?:no|number)|rechnung\s*(?:nr|nummer))\s*[:\-]?\s*([A-Za-z0-9\-_/]+)", re.IGNORECASE)


def _normalize_amount(raw_amount: str) -> Decimal:
    normalized = raw_amount.replace(".", "").replace(",", ".") if raw_amount.count(",") == 1 else raw_amount.replace(",", ".")
    return Decimal(normalized)


def _fallback_extract(text: str) -> ExtractedRecord:
    invoice_number = None
    currency = None
    total_amount = None

    invoice_match = INVOICE_PATTERN.search(text)
    if invoice_match:
        invoice_number = invoice_match.group(1).strip()

    currency_match = CURRENCY_PATTERN.search(text)
    if currency_match:
        currency = currency_match.group(1).upper()

    amount_match = AMOUNT_PATTERN.search(text)
    if amount_match:
        total_amount = _normalize_amount(amount_match.group(1))

    return ExtractedRecord(
        vendor_name=None,
        invoice_number=invoice_number,
        invoice_date=None,
        due_date=None,
        currency=currency,
        total_amount=total_amount,
        tax_amount=None,
        category="fallback-extraction",
        notes="Generated without LLM API",
    )


def _llm_extract(text: str) -> ExtractedRecord:
    client = OpenAI(api_key=settings.openai_api_key)
    prompt = (
        "Extract invoice-like structured data from the text. Return valid JSON with keys: "
        "vendor_name, invoice_number, invoice_date, due_date, currency, total_amount, tax_amount, category, notes. "
        "Use null when unknown. Dates must be YYYY-MM-DD. Numbers must be plain numeric values."
    )

    completion = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a strict information extraction engine."},
            {"role": "user", "content": f"{prompt}\n\nDocument text:\n{text[:15000]}"},
        ],
    )

    content = completion.choices[0].message.content
    payload = json.loads(content)
    return ExtractedRecord(**payload)


def transform_text_to_record(text: str) -> ExtractedRecord:
    if settings.openai_api_key:
        try:
            return _llm_extract(text)
        except Exception:
            return _fallback_extract(text)
    return _fallback_extract(text)
