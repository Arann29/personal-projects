from src.etl.transform import transform_text_to_record


def test_fallback_transform_extracts_basic_fields():
    text = """
    Vendor: Example Co
    Invoice Number: INV-123
    Currency: EUR
    Total Amount: 1299.95
    """
    record = transform_text_to_record(text)

    assert record.invoice_number == "INV-123"
    assert record.currency == "EUR"
    assert record.total_amount is not None
