from datetime import timedelta
from .recognizer import Recognizer
from ..models import AbstractPeriod, DatesRawData
from ..models.parser_models import FixPeriod
from ..partial_date.partial_datetime import PartialDateTime


# (1): Если указана часть суток в начале (редко используется, например, "вечером в 9").
# (2): Предлог времени ("в", "на", "до").
# (3): Четверть/половина (редко встречается).
# (4): Часы (например, "9h" или просто "h").
# (5): Число для часов.
# (6): "h" после числа.
# (7): Минуты (например, "30e" — "30 минут").
# (8): Число для минут.
# (9): Часть суток в конце ("вечера", "утра" и т.д.).

class TimeRecognizer(Recognizer):
    regex_pattern = r'([rvgd])?([fot])?(Q|H)?(h|(0)(h)?)((0)e?)?([rvgd])?'

    def parse_match(self, data: DatesRawData, match, now: PartialDateTime) -> bool:
        # Если нет значимых групп, выходим
        if not any([match.group(1), match.group(4), match.group(7), match.group(9)]):
            return False

        hours = None
        minutes = 0

        def safe_int(token_pos: int) -> int:
            """Безопасно извлекает целое число из токена."""
            try:
                token = data.tokens[token_pos]
                return int(token.value) if token.value.isdigit() else 0
            except (IndexError, ValueError, AttributeError):
                return 0

        if match.group(4):
            if match.group(5):
                hours = safe_int(match.start(5))
            elif match.group(4) == 'h':
                hours = 13

        # Обработка минут из group(7) (например, "30 минут")
        if match.group(7):
            minutes += safe_int(match.start(8))

        # Добавляем четверть/полчаса (Q/H)
        if match.group(3):
            minutes += 15 if match.group(3) == 'Q' else 30

        # Коррекция переполнения минут
        if minutes >= 60:
            if hours is None:
                hours = 0
            hours += minutes // 60
            minutes = minutes % 60

        date = AbstractPeriod()
        date.fix(FixPeriod.TIME_UNCERTAIN)
        if hours > 12:
            date.fix(FixPeriod.TIME)
        else:
            part = 'd'
            if match.group(9) is not None or match.group(1) is not None:
                part = match.group(9) if match.group(1) is None else match.group(1)
                date.fix(FixPeriod.TIME)
            else:
                date.fix(FixPeriod.TIME_UNCERTAIN)

            if part == 'd':
                if hours <= 4:
                    hours += 12
            elif part == 'v':
                if hours <= 11:
                    hours += 12
            elif part == 'g':
                if hours >= 10:
                    hours += 12

            if hours == 24:
                hours = 0

        # Создание временного интервала
        total_seconds = (hours * 3600 if hours is not None else 0) + minutes * 60
        date = AbstractPeriod()
        date.fix(FixPeriod.TIME)
        date.time = timedelta(seconds=total_seconds)

        # Замена токенов
        s, e = match.span()
        data.replace_tokens_by_dates(s, e - s, date)
        return True
