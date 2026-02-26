from src.parsers.diners_club import DinersClubParser
from src.parsers.mastercard_pacificard import MastercardPacificardParser


def test_mastercard_parser_extracts_transaction():
    parser = MastercardPacificardParser()
    content = "Fecha de la transacción 2024-12-22 a las 00:06\nMonto $ 44.00"
    parsed = parser.parse(content)

    assert parsed is not None
    txn_datetime, amount = parsed
    assert txn_datetime.year == 2024
    assert amount == 44.0


def test_diners_parser_extracts_transaction():
    parser = DinersClubParser()
    content = "Fecha: 2024-12-22 00:50\nValor: 84,86"
    parsed = parser.parse(content)

    assert parsed is not None
    txn_datetime, amount = parsed
    assert txn_datetime.month == 12
    assert amount == 84.86
