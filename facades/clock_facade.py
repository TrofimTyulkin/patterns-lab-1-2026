"""
Здесь необходимо реализовать Facade.

Фасад должен скрывать работу как минимум с:
- цифровым адаптером;
- ClockFormatter;
- ClockHistory.
"""

from datetime import datetime

from adapters.digital_clock_adapter import DigitalClockAdapter
from clocks.analog_clock import AnalogClock
from interfaces import BaseDigitalClock
from services import ClockFormatter, ClockHistory

class ClockFacade:
    def __init__(
        self,
        clock: BaseDigitalClock | None = None,
        formatter: ClockFormatter | None = None,
        history: ClockHistory | None = None,
    ) -> None:
        self._clock = clock if clock is not None else DigitalClockAdapter(AnalogClock())
        self._formatter = formatter if formatter is not None else ClockFormatter()
        self._history = history if history is not None else ClockHistory()

    def set_date_time(self, value: datetime) -> None:
        self._clock.set_date_time(value)
        self._history.add(self._clock.get_date_time())

    def get_date_time(self) -> datetime:
        return self._clock.get_date_time()

    def get_formatted(self, fmt: str | None = None) -> str:
        value = self.get_date_time()
        return self._formatter.format(value) if fmt is None else self._formatter.format(value, fmt)

    def get_history(self) -> tuple[datetime, ...]:
        return self._history.all()
