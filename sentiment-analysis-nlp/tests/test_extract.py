from src.etl.extract import detect_text_column


def test_detect_text_column():
    columns = ["id", "date", "text"]
    assert detect_text_column(columns) == "text"


def test_detect_text_column_case_insensitive():
    columns = ["Date", "Review", "Rating"]
    assert detect_text_column(columns) == "Review"
