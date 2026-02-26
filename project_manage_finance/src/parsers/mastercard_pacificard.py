import datetime
import re

from src.parsers.base import EmailParser


class MastercardPacificardParser(EmailParser):
    date_pattern = re.compile(r"\*?Fecha de la transacción\*?\s*(\d{4}-\d{2}-\d{2} a las \d{2}:\d{2})")
    amount_pattern = re.compile(r"\*?Monto\*?\s*\$\s*(\d+\.\d{2})")

    def parse(self, email_content: str) -> tuple[datetime.datetime, float] | None:
        date_match = self.date_pattern.search(email_content)
        amount_match = self.amount_pattern.search(email_content)

        if not date_match or not amount_match:
            return None

        txn_datetime = datetime.datetime.strptime(date_match.group(1), "%Y-%m-%d a las %H:%M")
        amount = float(amount_match.group(1))
        return txn_datetime, amount
