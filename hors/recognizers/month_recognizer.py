from datetime import datetime

from .recognizer import Recognizer
from ..dict import Keywords
from ..models import AbstractPeriod, DatesRawData
from ..models.parser_models import FixPeriod
from ..partial_date.partial_datetime import PartialDateTime
from ..utils import ParserUtils


class MonthRecognizer(Recognizer):
    regex_pattern = r'([usxy])?M'

    def parse_match(self, data: DatesRawData, match, now: datetime) -> bool:
        year = now.year
        year_fixed = False
        s, e = match.span()

        g1 = match.group(1) or ''
        m_str = data.tokens[s + len(g1)].value
        month = ParserUtils.find_index(m_str, Keywords.months()) + 1
        if month == 0:
            month = now.month

        month_past = month < now.month if now.month is not None else False
        month_future = month > now.month if now.month is not None else False

        if g1 is not None:
            if g1 == 's' and not month_past:
                year -= 1
            elif g1 == 'y' and month_past:
                year += 1
            elif g1 == 'x' and not month_future:
                year += 1

        date = AbstractPeriod(PartialDateTime(year, month))
        date.fix(FixPeriod.MONTH)
        if year_fixed:
            date.fix(FixPeriod.YEAR)

        data.replace_tokens_by_dates(s, (e - s), date)

        return True
