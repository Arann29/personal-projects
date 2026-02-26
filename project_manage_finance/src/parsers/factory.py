from src.parsers.base import EmailParser
from src.parsers.diners_club import DinersClubParser
from src.parsers.mastercard_pacificard import MastercardPacificardParser


class ParserFactory:
    @staticmethod
    def get_parser(subject_or_source: str) -> EmailParser:
        token = subject_or_source.lower()
        if "diners" in token:
            return DinersClubParser()
        return MastercardPacificardParser()
