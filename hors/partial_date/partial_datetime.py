import datetime
from datetime import timedelta


class PartialDateTime:
    def __init__(self,
                 year=None, month=None, day=None,
                 hour=None, minute=None, second=None, microsecond=None,
                 relative_offset=timedelta(0),
                 weekday: int = None):  # 0 - понедельник, 6 - воскресенье
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.relative_offset = relative_offset

        # Если год, месяц и день заданы, вычисляем базовый weekday и корректируем его с учётом offset.
        if year is not None and month is not None and day is not None:
            base_wd = datetime.datetime(year, month, day).weekday()
            offset_days = int(relative_offset.total_seconds() // (24 * 3600))
            self._weekday = (base_wd + offset_days) % 7
        else:
            self._weekday = weekday

    @property
    def weekday(self):
        return self._weekday

    @weekday.setter
    def weekday(self, value):
        self._weekday = value

    def is_complete(self):
        return None not in (self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond)

    def to_datetime(self):
        if not self.is_complete():
            raise ValueError("Невозможно преобразовать в datetime, т.к. не все компоненты определены")
        base_dt = datetime.datetime(self.year, self.month, self.day,
                                    self.hour, self.minute, self.second, self.microsecond)
        return base_dt + self.relative_offset

    def isoformat(self):
        try:
            return self.to_datetime().isoformat()
        except Exception:
            return str(self)

    @classmethod
    def now(cls):
        dt = datetime.datetime.now()
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)

    def replace(self, **kwargs):
        new_fields = {
            'year': kwargs.get('year', self.year),
            'month': kwargs.get('month', self.month),
            'day': kwargs.get('day', self.day),
            'hour': kwargs.get('hour', self.hour),
            'minute': kwargs.get('minute', self.minute),
            'second': kwargs.get('second', self.second),
            'microsecond': kwargs.get('microsecond', self.microsecond)
        }
        new_offset = kwargs.get('relative_offset', self.relative_offset)
        new_weekday = kwargs.get('weekday', self._weekday)
        return PartialDateTime(**new_fields,
                               relative_offset=new_offset,
                               weekday=new_weekday)

    def _apply_delta(self, delta: timedelta) -> 'PartialDateTime':
        # Если год, месяц и день известны, создаем базовый datetime.
        dt = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour if self.hour is not None else 0,
            self.minute if self.minute is not None else 0,
            self.second if self.second is not None else 0,
            self.microsecond if self.microsecond is not None else 0
        )
        new_dt = dt + delta
        # Для каждого компонента: если он был задан, обновляем его; иначе оставляем None.
        new_year = new_dt.year if self.year is not None else None
        new_month = new_dt.month if self.month is not None else None
        new_day = new_dt.day if self.day is not None else None
        new_hour = new_dt.hour if self.hour is not None else None
        new_minute = new_dt.minute if self.minute is not None else None
        new_second = new_dt.second if self.second is not None else None
        new_microsecond = new_dt.microsecond if self.microsecond is not None else None
        new_weekday = new_dt.weekday()  # дата известна, поэтому можно вычислить
        return PartialDateTime(new_year, new_month, new_day,
                               new_hour, new_minute, new_second, new_microsecond,
                               relative_offset=timedelta(0),
                               weekday=new_weekday)

    def __add__(self, other):
        if isinstance(other, PartialDateTime):
            other = other.to_timedelta()
        if isinstance(other, datetime.timedelta):
            if self.year is not None and self.month is not None and self.day is not None:
                return self._apply_delta(other)
            else:
                new_offset = self.relative_offset + other
                if self._weekday is not None:
                    offset_days = int(other.total_seconds() // (24 * 3600))
                    new_weekday = (self._weekday + offset_days) % 7
                else:
                    new_weekday = None
                return PartialDateTime(self.year, self.month, self.day,
                                       self.hour, self.minute, self.second, self.microsecond,
                                       relative_offset=new_offset,
                                       weekday=new_weekday)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, PartialDateTime):
            if self.is_complete() and other.is_complete():
                dt1 = self.to_datetime()
                dt2 = other.to_datetime()
                return dt1 - dt2
            else:
                return self - other.to_timedelta()
        elif isinstance(other, datetime.timedelta):
            if self.year is not None and self.month is not None and self.day is not None:
                return self._apply_delta(-other)
            else:
                new_offset = self.relative_offset - other
                if self._weekday is not None:
                    offset_days = int(other.total_seconds() // (24 * 3600))
                    new_weekday = (self._weekday - offset_days) % 7
                else:
                    new_weekday = None
                return PartialDateTime(self.year, self.month, self.day,
                                       self.hour, self.minute, self.second, self.microsecond,
                                       relative_offset=new_offset,
                                       weekday=new_weekday)
        return NotImplemented

    def _compare_components(self, other):
        fields = ['year', 'month', 'day', 'hour', 'minute', 'second', 'microsecond']
        for field in fields:
            a = getattr(self, field)
            b = getattr(other, field)
            if a is not None and b is not None:
                if a < b:
                    return -1
                elif a > b:
                    return 1
            # Если хотя бы один компонент не указан, считаем их равными и переходим к следующему
        if self.relative_offset < other.relative_offset:
            return -1
        elif self.relative_offset > other.relative_offset:
            return 1
        return 0

    def __eq__(self, other):
        if isinstance(other, PartialDateTime):
            return self._compare_components(other) == 0
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, PartialDateTime):
            return self._compare_components(other) == -1
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, PartialDateTime):
            comp = self._compare_components(other)
            return comp in (-1, 0)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, PartialDateTime):
            return self._compare_components(other) == 1
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, PartialDateTime):
            comp = self._compare_components(other)
            return comp in (0, 1)
        return NotImplemented

    def __str__(self):
        year = str(self.year) if self.year is not None else "????"
        month = f"{self.month:02d}" if self.month is not None else "??"
        day = f"{self.day:02d}" if self.day is not None else "??"
        hour = f"{self.hour:02d}" if self.hour is not None else "??"
        minute = f"{self.minute:02d}" if self.minute is not None else "??"
        second = f"{self.second:02d}" if self.second is not None else "??"
        microsecond = f"{self.microsecond:06d}" if self.microsecond is not None else "??????"
        base_str = f"{year}-{month}-{day} {hour}:{minute}:{second}.{microsecond}"
        if self.relative_offset != timedelta(0):
            base_str += f" + {self.relative_offset}"
        weekday_str = f", weekday={self.weekday}" if self.weekday is not None else ""
        return base_str + weekday_str

    def __repr__(self):
        return (f"PartialDateTime(year={self.year}, month={self.month}, day={self.day}, "
                f"hour={self.hour}, minute={self.minute}, second={self.second}, microsecond={self.microsecond}, "
                f"relative_offset={self.relative_offset}, weekday={self.weekday})")

    def merge(self, other):
        year = self.year if self.year is not None else other.year
        month = self.month if self.month is not None else other.month
        day = self.day if self.day is not None else other.day
        hour = self.hour if self.hour is not None else other.hour
        minute = self.minute if self.minute is not None else other.minute
        second = self.second if self.second is not None else other.second
        microsecond = self.microsecond if self.microsecond is not None else other.microsecond
        weekday = self.weekday if self.weekday is not None else other.weekday

        known = {
            'day': (year is not None and month is not None and day is not None),
            'hour': (hour is not None),
            'minute': (minute is not None),
            'second': (second is not None),
            'microsecond': (microsecond is not None)
        }

        def mask_offset(offset: timedelta, known):

            days = offset.days if not known['day'] else 0

            sec_total = offset.seconds
            hours = sec_total // 3600
            rem = sec_total % 3600
            minutes = rem // 60
            seconds_part = rem % 60

            if known['hour']:
                hours = 0

            if known['minute']:
                minutes = 0

            if known['second']:
                seconds_part = 0

            micro = offset.microseconds if not known['microsecond'] else 0

            return timedelta(days=days, seconds=hours * 3600 + minutes * 60 + seconds_part, microseconds=micro)

        offset1 = mask_offset(self.relative_offset, known) if self.relative_offset is not None else timedelta(0)
        offset2 = mask_offset(other.relative_offset, known) if other.relative_offset is not None else timedelta(0)
        merged_offset = offset1 + offset2

        new_date = PartialDateTime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            relative_offset=merged_offset,
            weekday=weekday
        )

        if new_date.is_complete():
            new_date = new_date + merged_offset

        return new_date

    def to_timedelta(self):
        days = self.day if self.day is not None else 0
        hours = self.hour if self.hour is not None else 0
        minutes = self.minute if self.minute is not None else 0
        seconds = self.second if self.second is not None else 0
        microseconds = self.microsecond if self.microsecond is not None else 0
        return datetime.timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds
        )
