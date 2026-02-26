import base64
import json
import re
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from PIL import Image, ImageOps
import pytesseract
from pytesseract import TesseractNotFoundError

from src.config import settings


TOTAL_PATTERN = re.compile(r"(?:total|amount|valor)\s*[:$]?\s*([0-9]+(?:[\.,][0-9]{1,2})?)", re.IGNORECASE)
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
ALT_DATE_PATTERN = re.compile(r"(\d{2}[/-]\d{2}[/-]\d{4})")
MERCHANT_LINE_PATTERN = re.compile(r"^[A-Za-z0-9\s\.&\-]{3,}$")


def _normalize_amount(raw: str) -> float:
    return float(raw.replace(",", "."))


def _normalize_date(raw_date: str | None) -> str | None:
    if raw_date is None:
        return None

    value = raw_date.strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        return value

    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _extract_merchant(raw_text: str) -> str | None:
    for line in raw_text.splitlines():
        cleaned = line.strip()
        if len(cleaned) < 3:
            continue
        if any(token in cleaned.lower() for token in ("total", "date", "fecha", "amount", "valor")):
            continue
        if MERCHANT_LINE_PATTERN.match(cleaned):
            return cleaned[:100]
    return None


def _finalize_payload(payload: dict, method: str) -> dict:
    merchant_conf = 0.85 if payload.get("merchant") else 0.25
    date_conf = 0.95 if payload.get("txn_date") else 0.2
    total_conf = 0.95 if payload.get("total") is not None else 0.2

    if method == "ocr":
        merchant_conf -= 0.15
        date_conf -= 0.15
        total_conf -= 0.15
    elif method == "regex":
        merchant_conf -= 0.3
        date_conf -= 0.3
        total_conf -= 0.3

    confidence_by_field = {
        "merchant": max(0.0, round(merchant_conf, 2)),
        "txn_date": max(0.0, round(date_conf, 2)),
        "total": max(0.0, round(total_conf, 2)),
    }
    confidence_score = round(sum(confidence_by_field.values()) / len(confidence_by_field), 2)

    payload["extraction_method"] = method
    payload["confidence_by_field"] = confidence_by_field
    payload["confidence_score"] = confidence_score
    payload["requires_review"] = confidence_score < 0.75 or not _is_usable(payload)
    return payload


def _fallback_extract(raw_text: str) -> dict:
    total_match = TOTAL_PATTERN.search(raw_text)
    date_match = DATE_PATTERN.search(raw_text)
    alt_date_match = ALT_DATE_PATTERN.search(raw_text)

    total = _normalize_amount(total_match.group(1)) if total_match else None
    txn_date = _normalize_date(date_match.group(1) if date_match else (alt_date_match.group(1) if alt_date_match else None))
    merchant = _extract_merchant(raw_text)

    payload = {
        "merchant": merchant,
        "txn_date": txn_date,
        "total": total,
        "currency": "USD",
        "items": [],
        "raw_text": raw_text,
    }
    return _finalize_payload(payload, method="regex")


def _ocr_extract(image_path: str) -> dict:
    image = Image.open(image_path)
    gray = ImageOps.grayscale(image)
    enhanced = ImageOps.autocontrast(gray)
    text = pytesseract.image_to_string(enhanced)
    payload = _fallback_extract(text)
    return _finalize_payload(payload, method="ocr")


def _llm_extract(image_path: str) -> dict:
    client = OpenAI(api_key=settings.openai_api_key)
    image_bytes = Path(image_path).read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    completion = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Extract receipt data. Return strict JSON."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract merchant, txn_date (YYYY-MM-DD), total, currency, and items[] from this receipt. "
                            "Return JSON keys: merchant, txn_date, total, currency, items, raw_text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        },
                    },
                ],
            },
        ],
    )

    payload = json.loads(completion.choices[0].message.content)
    payload["txn_date"] = _normalize_date(payload.get("txn_date"))
    payload["raw_text"] = payload.get("raw_text") or ""
    payload.setdefault("currency", "USD")
    payload.setdefault("items", [])
    return _finalize_payload(payload, method="llm")


def _is_usable(payload: dict) -> bool:
    return payload.get("total") is not None and payload.get("txn_date") is not None


def extract_receipt(image_path: str) -> dict:
    if settings.openai_api_key:
        try:
            llm_payload = _llm_extract(image_path)
            if _is_usable(llm_payload):
                return llm_payload
        except Exception:
            pass

    try:
        ocr_payload = _ocr_extract(image_path)
        return ocr_payload
    except TesseractNotFoundError:
        return _fallback_extract(Path(image_path).stem)
    except Exception:
        return _fallback_extract(Path(image_path).stem)
