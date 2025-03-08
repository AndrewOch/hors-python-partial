# Hors

[![MIT License](https://img.shields.io/pypi/l/aiogram.svg?style=flat-square)](https://opensource.org/licenses/MIT)

**hors** — это модуль Python для распознавания дат и времени в естественной речи на русском языке. Он умеет понимать
сложные конструкции с абсолютными и относительными датами, временем, а также временными периодами. Название библиотеки
отсылает к славянскому богу солнца – [Хорс](https://ru.wikipedia.org/wiki/%D0%A5%D0%BE%D1%80%D1%81).

> Оригинальная версия библиотеки написана Денисом Пешехоновым на C# и доступна
> на [GitHub](https://github.com/DenisNP/Hors) под лицензией MIT. Логика работы в форке почти не изменена, за
> исключением ряда доработок.

## Отличия от оригинальной библиотеки


**Особенности PartialDateTime**
- Гибкость задания: Можно задавать дату с любым набором известных компонентов (год, месяц, день, время). Если время не задано, оно может оставаться неопределённым.
- Арифметика по известным разрядам: При прибавлении или вычитании timedelta операции применяются только к тем компонентам, которые известны. Например, если указана только дата без времени, то операция применяется к дате (год, месяц, день), а время в результате остаётся неопределенным.

## Установка

Для установки клонируйте репозиторий и установите зависимости вручную:

```bash
git clone https://github.com/yourusername/hors-python-partial.git
cd hors-python
pip install -r requirements.txt
python setup.py install
```

## Использование

Пример использования библиотеки:

```python
import hors

# Распознавание фиксированной даты и времени
r = hors.process_phrase('Утром 3 сентября 2059 года мы слушали Шуфутинского')
print(r.dates[0].type)  # <DateTimeTokenType.FIXED: 1>
print(r.dates[0].date_from)  # Например, PartialDateTime(year=2059, month=9, day=3, hour=9)

# Распознавание временного периода
r = hors.process_phrase('Полёт Гагарина длился с 9 утра 12 апреля 1961 года до 11 утра')
print(r.dates[0].type)  # <DateTimeTokenType.PERIOD: 2>
print(r.dates[0].date_from)  # PartialDateTime(year=1961, month=4, day=12, hour=9)
print(r.dates[0].date_to)  # PartialDateTime(year=1961, month=4, day=12, hour=11)

r = hors.process_phrase('3 числа мы слушали Шуфутинского')
print(r.dates[0].type)  # <DateTimeTokenType.FIXED: 1>
print(f"{r.dates[0].date_from} | {r.dates[0].date_to}")
# ????-??-03 00:00:00.000000 | ????-??-03 00:00:00.000000 + 23:59:59.999999
```

## Тестирование

Запустите тесты командой:
```bash
python -m unittest discover tests
```
