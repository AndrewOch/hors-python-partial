import datetime
from typing import List
from calendar import monthrange

from ..dict import Morph


class ParserUtils:

    @staticmethod
    def find_index(t: str, l: List[List[str]]) -> int:
        for i, sublist in enumerate(l):
            if Morph.has_one_of_lemmas(t, sublist):
                return i
        return -1

    @staticmethod
    def get_year_from_number(n: int, current_year: int = None) -> int:
        """
        Определяет полный год по сокращённому числу n относительно current_year.

        Если current_year не задан, используется текущий календарный год.

        Примеры:
         - При current_year = 2025 (первая половина века):
              n >= 40 → год прошлого века (например, 41 → 1941, 93 → 1993),
              иначе n → 2000 + n.
         - При current_year = 2089 (вторая половина века):
              любые двухзначные числа трактуются как текущего века
              (например, 45 → 2045, 1 → 2001, 90 → 2090).
        """
        if current_year is None:
            current_year = datetime.datetime.now().year
        if n >= 100:
            return n
        current_century = current_year // 100
        if current_year % 100 < 50:
            if n >= 40:
                return (current_century - 1) * 100 + n
            else:
                return current_century * 100 + n
        else:
            return current_century * 100 + n

    @staticmethod
    def get_day_valid_for_month(year: int, month: int, day: int) -> int:
        if year is None or month is None:
            return min(day, 31)
        _, days_in_month = monthrange(year, month)
        if day > days_in_month:
            raise ValueError(f"Invalid day {day} for month {month} in year {year} (max {days_in_month})")
        return max(1, day)
