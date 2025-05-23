import unittest
from datetime import timedelta

from hors import process_phrase
from hors.models.parser_models import DateTimeTokenType
from hors.partial_date.partial_datetime import PartialDateTime


class BaseHorsTests(unittest.TestCase):

    def test_no_dates(self):
        result = process_phrase('в день, какой неведомо, в никаком году')
        self.assertEqual(0, len(result.dates))

    def test_january(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase('10 января событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(2020, date.date_from.year)

    def test_time_period_before_day(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase('с 5 до 7 вечера в понедельник будет событие', starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(17, date.date_from.hour)
        self.assertEqual(19, date.date_to.hour)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(14, date.date_to.day)

    def test_time_period_simple(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase('с 10 до 13 событие', starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(10, date.date_from.hour)
        self.assertEqual(13, date.date_to.hour)

    def test_daytime(self):
        starting_point = PartialDateTime(2019, 10, 14)
        result = process_phrase('Завтра в час обед и продлится он час с небольшим', starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(13, date.date_from.hour)

    def test_nighttime(self):
        starting_point = PartialDateTime(2020, 1, 1)
        result = process_phrase(
            'Завтра в 2 ночи полнолуние, а затем в 3 часа ночи новолуние и наконец в 12 часов ночи игра.',
            starting_point)
        print(result)

        self.assertEqual(3, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(2, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(3, date.date_from.hour)

        date = result.dates[2]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(0, date.date_from.hour)
        self.assertEqual(1, date.date_from.day)

    def test_long_period(self):
        starting_point = PartialDateTime(2019, 10, 14)
        result = process_phrase(
            'С вечера следующей среды до четверти 10 утра понедельника в декабре можно будет наблюдать снег',
            starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(23, date.date_from.day)
        self.assertEqual(10, date.date_from.month)
        self.assertEqual(2, date.date_to.day)
        self.assertEqual(12, date.date_to.month)
        self.assertEqual(9, date.date_to.hour)
        self.assertEqual(15, date.date_to.minute)

    def test_collapse_complex(self):
        starting_point = PartialDateTime(2025, 3, 8)
        result = process_phrase('В понедельник в 9 и 10 вечера', starting_point)
        print(result)
        print(result.dates[0].date_from.hour)

        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2025, date.date_from.year)
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(21, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(22, date.date_from.hour)

        result = process_phrase('В понедельник в 10 и 9 вечера', starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2025, date.date_from.year)
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(22, date.date_from.hour)

        date = result.dates[1]
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(21, date.date_from.hour)

    def test_multiple_simple(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase(
            'Позавчера в 6:30 состоялось совещание, а завтра днём будет хорошая погода.',
            starting_point)
        self.assertEqual(2, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(11, date.date_from.day)
        self.assertEqual(6, date.date_from.hour)
        self.assertEqual(30, date.date_from.minute)

        date = result.dates[1]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(True, date.has_time)

    def test_collapse_direction(self):
        starting_point = PartialDateTime(2019, 10, 15)
        strings = [
            'В следующем месяце с понедельника буду ходить в спортзал!',
            'С понедельника в следующем месяце буду ходить в спортзал!',
        ]
        for s in strings:
            result = process_phrase(s, starting_point)
            self.assertEqual(1, len(result.dates))

            date = result.dates[0]
            self.assertEqual(2019, date.date_from.year)
            self.assertEqual(4, date.date_from.day)
            self.assertEqual(11, date.date_from.month)

    def test_weekday(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase('В следующем месяце во вторник состоится событие', starting_point)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(5, date.date_from.day)
        self.assertEqual(11, date.date_from.month)

        result = process_phrase('Через месяц во вторник состоится событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(11, date.date_from.month)

    def test_time_after_day(self):
        starting_point = PartialDateTime(2019, 10, 8)
        result = process_phrase('в четверг 16 0 0 будет событие', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(16, date.date_from.hour)
        self.assertEqual(10, date.date_from.day)

    def test_time_period(self):
        starting_point = PartialDateTime(2019, 9, 7)
        result = process_phrase('В следующий четверг с 9 утра до 6 вечера важный экзамен!', starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(True, date.has_time)
        self.assertEqual(9, date.date_from.hour)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(18, date.date_to.hour)
        self.assertEqual(12, date.date_to.day)
        self.assertEqual(9, date.date_to.month)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(2019, date.date_to.year)

    def test_complex_period(self):
        starting_point = PartialDateTime(2019, 7, 7)
        result = process_phrase('хакатон с 12 часов 18 сентября до 12 часов 20 сентября', starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(12, date.date_from.hour)
        self.assertEqual(18, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(12, date.date_to.hour)
        self.assertEqual(20, date.date_to.day)
        self.assertEqual(9, date.date_to.month)
        self.assertEqual(2019, date.date_from.year)
        self.assertEqual(2019, date.date_to.year)

    def test_time_before_day(self):
        starting_point = PartialDateTime(2019, 9, 7)
        result = process_phrase('В 12 часов 12 сентября будет встреча', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(12, date.date_from.hour)
        self.assertEqual(12, date.date_from.day)
        self.assertEqual(9, date.date_from.month)

    def test_time_hour_of_day(self):
        starting_point = PartialDateTime(2019, 9, 7)
        result = process_phrase('24 сентября в час дня', starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(True, date.has_time)
        self.assertEqual(13, date.date_from.hour)
        self.assertEqual(24, date.date_from.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(2019, date.date_from.year)

    def test_fix_period(self):
        starting_point = PartialDateTime(2019, 9, 7)
        result = process_phrase('на выходных будет хорошо', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(15, date.date_to.day)

    def test_dates_period(self):
        starting_point = PartialDateTime(2019, 8, 6)
        strings = [
            'с 11 по 15 сентября будет командировка',
            'от 11 по 15 сентября будет командировка',
            'с 11 до 15 сентября будет командировка',
        ]
        for s in strings:
            result = process_phrase(s, starting_point)
            self.assertEqual(1, len(result.dates))

            date = result.dates[0]
            self.assertEqual(DateTimeTokenType.PERIOD, date.type)
            self.assertEqual(11, date.date_from.day)
            self.assertEqual(15, date.date_to.day)
            self.assertEqual(9, date.date_from.month)
            self.assertEqual(9, date.date_to.month)

        starting_point = PartialDateTime(2019, 9, 6)
        result = process_phrase('с 11 до 15 числа будет командировка', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(11, date.date_from.day)
        self.assertEqual(15, date.date_to.day)
        self.assertEqual(9, date.date_from.month)
        self.assertEqual(9, date.date_to.month)

    def test_days_of_week(self):
        starting_point = PartialDateTime(2019, 9, 6)
        result = process_phrase('во вторник встреча с заказчиком', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(10, date.date_from.day)

    def test_holidays(self):
        starting_point = PartialDateTime(2019, 9, 2)
        result = process_phrase('в эти выходные еду на дачу', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(7, date.date_from.day)
        self.assertEqual(8, date.date_to.day)

    def test_holiday(self):
        starting_point = PartialDateTime(2019, 9, 2)
        result = process_phrase('пойду гулять в следующий выходной', starting_point)
        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.FIXED, date.type)
        self.assertEqual(14, date.date_from.day)
        self.assertEqual(14, date.date_to.day)

    def test_from_to_reversed(self):
        starting_point = PartialDateTime(2019, 10, 13)
        result = process_phrase('с 2 до 5', starting_point)
        print(result)

        self.assertEqual(1, len(result.dates))

        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        date_from = date.date_from
        date_to = date.date_to
        self.assertEqual(14, date_from.hour)
        self.assertEqual(17, date_to.hour)
        self.assertEqual(13, date_from.day)
        self.assertEqual(13, date_to.day)

    def test_year_and_hour_only(self):
        """Проверка распознавания даты с известным годом и часом."""
        result = process_phrase("В 2025 году в 15 часов")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(2025, date.date_from.year)
        self.assertIsNone(date.date_from.month)
        self.assertIsNone(date.date_from.day)
        self.assertEqual(15, date.date_from.hour)

    def test_month_and_day_only(self):
        """Проверка распознавания даты с известным месяцем и днем, но без года."""
        result = process_phrase("10 января")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertIsNone(date.date_from.year)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(0, date.date_from.hour)
        self.assertEqual(0, date.date_from.minute)
        self.assertEqual(0, date.date_from.second)
        self.assertEqual(0, date.date_from.microsecond)

        self.assertEqual(86399, date.date_to.relative_offset.seconds)

    def test_time_only(self):
        """Проверка распознавания только времени без даты."""
        result = process_phrase("в 14:30")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertIsNone(date.date_from.year)
        self.assertIsNone(date.date_from.month)
        self.assertIsNone(date.date_from.day)
        self.assertEqual(14, date.date_from.hour)
        self.assertEqual(30, date.date_from.minute)

    def test_relative_offset_with_time(self):
        """Проверка распознавания относительного смещения с временем."""
        result = process_phrase("через 2 дня в 10 утра")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertIsNone(date.date_from.year)
        self.assertIsNone(date.date_from.month)
        self.assertIsNone(date.date_from.day)
        self.assertEqual(10, date.date_from.hour)
        self.assertEqual(timedelta(days=2), date.date_from.relative_offset)

    def test_period_with_partial_dates(self):
        """Проверка распознавания периода с неполными датами."""
        result = process_phrase("с 10 до 15 января")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertIsNone(date.date_from.year)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(10, date.date_from.day)
        self.assertEqual(0, date.date_from.hour)
        self.assertEqual(0, date.date_from.minute)
        self.assertEqual(0, date.date_from.second)
        self.assertEqual(0, date.date_from.microsecond)

        self.assertIsNone(date.date_to.year)
        self.assertEqual(1, date.date_to.month)
        self.assertEqual(15, date.date_to.day)
        self.assertEqual(0, date.date_to.hour)
        self.assertEqual(0, date.date_to.minute)
        self.assertEqual(0, date.date_to.second)
        self.assertEqual(0, date.date_to.microsecond)
        self.assertEqual(86399, date.date_to.relative_offset.seconds)

    def test_no_starting_point(self):
        """Проверка работы без starting_point с полностью неизвестной датой."""
        result = process_phrase("завтра")
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertIsNone(date.date_from.year)
        self.assertIsNone(date.date_from.month)
        self.assertIsNone(date.date_from.day)

        self.assertEqual(0, date.date_from.hour)
        self.assertEqual(0, date.date_from.minute)
        self.assertEqual(0, date.date_from.second)
        self.assertEqual(0, date.date_from.microsecond)
        self.assertEqual(timedelta(days=1), date.date_from.relative_offset)

    def test_next_week(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("на следующей неделе", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2023, date.date_from.year)
        self.assertEqual(5, date.date_from.month)
        self.assertEqual(29, date.date_from.day)
        self.assertEqual(2023, date.date_to.year)
        self.assertEqual(6, date.date_to.month)
        self.assertEqual(4, date.date_to.day)

    def test_last_week(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("на прошлой неделе", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2023, date.date_from.year)
        self.assertEqual(5, date.date_from.month)
        self.assertEqual(15, date.date_from.day)
        self.assertEqual(2023, date.date_to.year)
        self.assertEqual(5, date.date_to.month)
        self.assertEqual(21, date.date_to.day)

    def test_next_month(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("в следующем месяце", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2023, date.date_from.year)
        self.assertEqual(6, date.date_from.month)
        self.assertEqual(1, date.date_from.day)
        self.assertEqual(2023, date.date_to.year)
        self.assertEqual(6, date.date_to.month)
        self.assertEqual(30, date.date_to.day)
        self.assertIsNone(date.date_from.hour)
        self.assertIsNone(date.date_to.hour)

    def test_last_month(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("в прошлом месяце", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2023, date.date_from.year)
        self.assertEqual(4, date.date_from.month)
        self.assertEqual(1, date.date_from.day)
        self.assertEqual(2023, date.date_to.year)
        self.assertEqual(4, date.date_to.month)
        self.assertEqual(30, date.date_to.day)
        self.assertIsNone(date.date_from.hour)
        self.assertIsNone(date.date_to.hour)

    def test_next_year(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("в следующем году", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2024, date.date_from.year)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(1, date.date_from.day)
        self.assertEqual(2024, date.date_to.year)
        self.assertEqual(12, date.date_to.month)
        self.assertEqual(31, date.date_to.day)
        self.assertIsNone(date.date_from.hour)
        self.assertIsNone(date.date_to.hour)

    def test_last_year(self):
        starting_point = PartialDateTime(2023, 5, 22)
        result = process_phrase("в прошлом году", starting_point)
        print(result)
        self.assertEqual(1, len(result.dates))
        date = result.dates[0]
        self.assertEqual(DateTimeTokenType.PERIOD, date.type)
        self.assertEqual(2022, date.date_from.year)
        self.assertEqual(1, date.date_from.month)
        self.assertEqual(1, date.date_from.day)
        self.assertEqual(2022, date.date_to.year)
        self.assertEqual(12, date.date_to.month)
        self.assertEqual(31, date.date_to.day)
        self.assertIsNone(date.date_from.hour)
        self.assertIsNone(date.date_to.hour)


if __name__ == '__main__':
    unittest.main()
