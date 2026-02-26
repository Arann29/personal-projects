from src.ingestion import receipt


def test_extract_receipt_uses_ocr_when_no_llm(monkeypatch):
    monkeypatch.setattr(receipt.settings, "openai_api_key", None)

    def fake_ocr_extract(_image_path: str) -> dict:
        return {
            "merchant": "BILLA",
            "txn_date": "2026-02-25",
            "total": 12.4,
            "currency": "USD",
            "items": [],
            "raw_text": "BILLA\nTOTAL 12.40\n2026-02-25",
            "extraction_method": "ocr",
            "confidence_score": 0.8,
            "confidence_by_field": {"merchant": 0.7, "txn_date": 0.8, "total": 0.9},
            "requires_review": False,
        }

    monkeypatch.setattr(receipt, "_ocr_extract", fake_ocr_extract)

    payload = receipt.extract_receipt("dummy_receipt.jpg")

    assert payload["merchant"] == "BILLA"
    assert payload["total"] == 12.4
    assert payload["txn_date"] == "2026-02-25"
    assert payload["confidence_score"] >= 0.7
    assert payload["requires_review"] is False


def test_fallback_extract_parses_text_patterns():
    payload = receipt._fallback_extract("My Store\nFecha 2026-02-26\nTotal: 45.70")

    assert payload["merchant"] == "My Store"
    assert payload["txn_date"] == "2026-02-26"
    assert payload["total"] == 45.7
    assert payload["extraction_method"] == "regex"
    assert "confidence_by_field" in payload
    assert isinstance(payload["requires_review"], bool)
