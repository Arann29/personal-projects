from src.etl.extract import extract_text


def test_extract_text_from_txt():
    raw = b"Invoice Number: INV-9"
    text = extract_text(raw, "invoice.txt")
    assert "INV-9" in text
