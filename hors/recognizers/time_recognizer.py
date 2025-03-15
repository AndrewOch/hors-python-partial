from datetime import timedelta
from .recognizer import Recognizer
from ..models import AbstractPeriod, DatesRawData
from ..models.parser_models import FixPeriod
from ..partial_date.partial_datetime import PartialDateTime


class TimeRecognizer(Recognizer):
    regex_pattern = r'([rvgd])?([fot])?(Q|H)?(h|(0)(h)?)((0)e?)?([rvgd])?'

    def parse_match(self, data: DatesRawData, match, now: PartialDateTime) -> bool:
        # Если нет значимых групп, выходим
        if not any([match.group(1), match.group(4), match.group(7), match.group(9)]):
            return False

        hours = None
        minutes = 0

        # Обработка group(4): '0h' (часы) или '0' (минуты)
        if match.group(4):
            if 'h' in match.group(4):  # Часы (например, "1 час")
                hours = int(data.tokens[match.start(5)].value)
            else:  # Только минуты (например, "14 минут")
                minutes = int(data.tokens[match.start(5)].value)

        # Обработка минут из group(7) (например, "30 минут")
        if match.group(7):
            minutes += int(data.tokens[match.start(8)].value)

        # Добавляем четверть/полчаса (Q/H)
        if match.group(3):
            minutes += 15 if match.group(3) == 'Q' else 30

        # Коррекция переполнения минут
        if minutes >= 60:
            if hours is None:
                hours = 0
            hours += minutes // 60
            minutes = minutes % 60

        # Создание временного интервала
        total_seconds = (hours * 3600 if hours is not None else 0) + minutes * 60
        date = AbstractPeriod()
        date.fix(FixPeriod.TIME)
        date.time = timedelta(seconds=total_seconds)

        # Замена токенов
        s, e = match.span()
        data.replace_tokens_by_dates(s, e - s, date)
        return True
