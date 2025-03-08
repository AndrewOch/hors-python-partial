from .recognizer import Recognizer
from ..models import AbstractPeriod, DatesRawData
from ..models.parser_models import FixPeriod
from ..partial_date.partial_datetime import PartialDateTime
from ..utils import ParserUtils


class YearRecognizer(Recognizer):
    regex_pattern = r'(1)Y?|(0)Y'

    def parse_match(self, data: DatesRawData, match, now) -> bool:
        s, e = match.span()
        try:
            n = int(data.tokens[s].value)
        except ValueError:
            n = 0
        year = ParserUtils.get_year_from_number(n, now.year)
        date = AbstractPeriod(PartialDateTime(year))
        date.fix(FixPeriod.YEAR)
        data.replace_tokens_by_dates(s, (e - s), date)
        return True
