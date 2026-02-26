from src.categorization.pipeline import classify_transaction


def test_classifies_transport_keyword():
    category = classify_transaction("Uber ride to office")
    assert category == "Transport"


def test_classifies_other_when_no_match():
    category = classify_transaction("Unknown merchant purchase")
    assert category == "Other"
