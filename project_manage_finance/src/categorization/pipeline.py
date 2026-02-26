import re

from src.categorization.rules import RULES


def classify_transaction(description: str, merchant: str | None = None) -> str:
    text = f"{description} {merchant or ''}".lower()
    for rule in RULES:
        if re.search(rule.pattern, text):
            return rule.category
    return "Other"
