"""
Adapter: позволяет использовать аналоговые часы (BaseAnalogClock)
там, где клиент ожидает цифровой интерфейс (BaseDigitalClock).
"""

from datetime import datetime

from consts import DayNightDivision
from interfaces import BaseAnalogClock, BaseDigitalClock

DEGREES_PER_HOUR = 360 / 12  # часовая стрелка: 30° за час
DEGREES_PER_MINUTE = 360 / 60  # минутная стрелка: 6° за минуту
DEGREES_PER_SECOND = 360 / 60  # секундная стрелка: 6° за секунду


class DigitalClockAdapter(BaseDigitalClock):
    """
    Объектный адаптер: реализует BaseDigitalClock, делегируя хранение
    времени аналоговым часам, переданным через композицию.

    Аналоговые часы показывают время с точностью до секунды,
    поэтому микросекунды и часовой пояс при установке отбрасываются.
    """

    def __init__(self, clock: BaseAnalogClock) -> None:
        self._clock = clock

    def set_date_time(self, date: datetime) -> None:
        hour, minute, second = date.hour, date.minute, date.second

        division = DayNightDivision.AM if hour < 12 else DayNightDivision.PM

        second_angle = second * DEGREES_PER_SECOND
        minute_angle = (minute + second / 60) * DEGREES_PER_MINUTE
        hour_angle = (hour % 12 + minute / 60 + second / 3600) * DEGREES_PER_HOUR

        self._clock.set_date_time(
            year=date.year,
            month=date.month,
            day=date.day,
            hour_angle=hour_angle,
            minute_angle=minute_angle,
            second_angle=second_angle,
            day_night_division=division,
        )

    def get_date_time(self) -> datetime:
        second = round(self._clock.get_second_angle() / DEGREES_PER_SECOND) % 60

        minute_angle = self._clock.get_minute_angle() - second / 60 * DEGREES_PER_MINUTE
        minute = round(minute_angle / DEGREES_PER_MINUTE) % 60

        hour_angle = (self._clock.get_hour_angle() - (minute / 60 + second / 3600) * DEGREES_PER_HOUR)
        hour = round(hour_angle / DEGREES_PER_HOUR) % 12

        # 12-часовой циферблат: 0° + AM — полночь (00), 0° + PM — полдень (12).
        if self._clock.get_day_night_division() is DayNightDivision.PM:
            hour += 12

        return datetime(
            self._clock.get_year(),
            self._clock.get_month(),
            self._clock.get_day(),
            hour,
            minute,
            second,
        )
