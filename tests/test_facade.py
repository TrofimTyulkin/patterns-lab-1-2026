from datetime import datetime

import pytest

from facades import ClockFacade
from interfaces import BaseDigitalClock
from services import ClockFormatter, ClockHistory


class StubDigitalClock(BaseDigitalClock):
    """Цифровые часы без адаптера: хранят datetime как есть."""

    def __init__(self) -> None:
        self.value = datetime(2000, 1, 1)

    def set_date_time(self, date: datetime) -> None:
        self.value = date

    def get_date_time(self) -> datetime:
        return self.value


class SpyFormatter(ClockFormatter):
    def __init__(self) -> None:
        self.calls: list[tuple[datetime, str]] = []

    def format(self, value: datetime, fmt: str = "%d.%m.%Y %H:%M:%S") -> str:
        self.calls.append((value, fmt))
        return "formatted"


class SizedHistory(ClockHistory):
    """История с __len__: пустая она ложна в bool-контексте."""

    def __len__(self) -> int:
        return len(self.all())


@pytest.fixture
def facade() -> ClockFacade:
    return ClockFacade()


def test_set_and_get_date_time(facade: ClockFacade) -> None:
    value = datetime(2026, 9, 24, 12, 34, 56)

    facade.set_date_time(value)

    assert facade.get_date_time() == value


def test_set_overwrites_previous_value(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 1, 2, 3))
    facade.set_date_time(datetime(2026, 9, 25, 22, 0, 0))

    assert facade.get_date_time() == datetime(2026, 9, 25, 22, 0, 0)


def test_formatted_default(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 12, 34, 56))

    assert facade.get_formatted() == "24.09.2026 12:34:56"


def test_formatted_custom(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 0, 5, 0))

    assert facade.get_formatted("%H:%M") == "00:05"


def test_history_is_empty_initially(facade: ClockFacade) -> None:
    assert facade.get_history() == ()


def test_history_keeps_order(facade: ClockFacade) -> None:
    values = [
        datetime(2026, 9, 24, 0, 0, 0),
        datetime(2026, 9, 24, 12, 0, 0),
        datetime(2026, 9, 24, 23, 59, 59),
    ]

    for value in values:
        facade.set_date_time(value)

    assert facade.get_history() == tuple(values)


def test_history_records_repeated_values(facade: ClockFacade) -> None:
    value = datetime(2026, 9, 24, 12, 0, 0)

    facade.set_date_time(value)
    facade.set_date_time(value)

    assert facade.get_history() == (value, value)


def test_getters_do_not_change_history(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 12, 0, 0))

    facade.get_date_time()
    facade.get_formatted()
    facade.get_history()

    assert len(facade.get_history()) == 1


def test_history_stores_value_shown_by_clock(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 12, 0, 0, 999999))

    assert facade.get_history() == (datetime(2026, 9, 24, 12, 0, 0),)


def test_history_is_immutable_tuple(facade: ClockFacade) -> None:
    facade.set_date_time(datetime(2026, 9, 24, 12, 0, 0))

    history = facade.get_history()

    assert isinstance(history, tuple)
    with pytest.raises(AttributeError):
        history.append(datetime(2026, 1, 1))  # type: ignore[attr-defined]


def test_facade_works_with_any_digital_clock() -> None:
    stub = StubDigitalClock()
    facade = ClockFacade(clock=stub)
    value = datetime(2026, 9, 24, 12, 34, 56, 789)

    facade.set_date_time(value)

    assert stub.value == value
    assert facade.get_date_time() == value
    assert facade.get_history() == (value,)


def test_facade_delegates_formatting() -> None:
    formatter = SpyFormatter()
    facade = ClockFacade(clock=StubDigitalClock(), formatter=formatter)
    value = datetime(2026, 9, 24, 12, 0, 0)
    facade.set_date_time(value)

    assert facade.get_formatted("%Y") == "formatted"
    assert formatter.calls == [(value, "%Y")]


def test_facade_uses_injected_empty_history() -> None:
    # Пустая SizedHistory ложна: с `history or ClockHistory()` фасад
    # молча подменил бы её своей историей.
    history = SizedHistory()
    facade = ClockFacade(clock=StubDigitalClock(), history=history)
    value = datetime(2026, 9, 24, 12, 0, 0)

    facade.set_date_time(value)

    assert history.all() == (value,)
