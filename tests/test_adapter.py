from datetime import datetime, timedelta

import pytest

from adapters import DigitalClockAdapter
from client.digital_clock_display import DigitalClockDisplay
from clocks import AnalogClock
from consts import DayNightDivision
from interfaces import BaseDigitalClock

AM = DayNightDivision.AM
PM = DayNightDivision.PM


@pytest.fixture
def analog() -> AnalogClock:
    return AnalogClock()


@pytest.fixture
def adapter(analog: AnalogClock) -> DigitalClockAdapter:
    return DigitalClockAdapter(analog)


@pytest.mark.parametrize(
    ("time", "hour_angle", "minute_angle", "second_angle", "division"),
    [
        ((0, 0, 0), 0.0, 0.0, 0.0, AM),  # полночь
        ((12, 0, 0), 0.0, 0.0, 0.0, PM),  # полдень
        ((3, 0, 0), 90.0, 0.0, 0.0, AM),
        ((15, 30, 0), 105.0, 180.0, 0.0, PM),
        ((6, 15, 30), 187.75, 93.0, 180.0, AM),
        ((0, 0, 30), 0.25, 3.0, 180.0, AM),
        ((11, 59, 59), 359.991667, 359.9, 354.0, AM),
        ((12, 59, 59), 29.991667, 359.9, 354.0, PM),
        ((13, 0, 0), 30.0, 0.0, 0.0, PM),
        ((23, 59, 59), 359.991667, 359.9, 354.0, PM),
    ],
)
def test_set_converts_datetime_to_angles(
    adapter: DigitalClockAdapter,
    analog: AnalogClock,
    time: tuple[int, int, int],
    hour_angle: float,
    minute_angle: float,
    second_angle: float,
    division: DayNightDivision,
) -> None:
    adapter.set_date_time(datetime(2026, 9, 24, *time))

    assert analog.get_hour_angle() == pytest.approx(hour_angle, abs=1e-6)
    assert analog.get_minute_angle() == pytest.approx(minute_angle)
    assert analog.get_second_angle() == pytest.approx(second_angle)
    assert analog.get_day_night_division() is division


@pytest.mark.parametrize(
    ("hour_angle", "minute_angle", "second_angle", "division", "expected"),
    [
        (0.0, 0.0, 0.0, AM, (0, 0, 0)),
        (0.0, 0.0, 0.0, PM, (12, 0, 0)),
        (90.0, 0.0, 0.0, AM, (3, 0, 0)),
        (105.0, 180.0, 0.0, PM, (15, 30, 0)),
        (187.75, 93.0, 180.0, AM, (6, 15, 30)),
        (359.9916666666666, 359.9, 354.0, PM, (23, 59, 59)),
    ],
)
def test_get_converts_angles_to_datetime(
    adapter: DigitalClockAdapter,
    analog: AnalogClock,
    hour_angle: float,
    minute_angle: float,
    second_angle: float,
    division: DayNightDivision,
    expected: tuple[int, int, int],
) -> None:
    analog.set_date_time(2026, 9, 24, hour_angle, minute_angle, second_angle, division)

    assert adapter.get_date_time() == datetime(2026, 9, 24, *expected)


@pytest.mark.parametrize(
    "value",
    [
        datetime(2026, 9, 24, 0, 0, 0),
        datetime(2026, 9, 24, 0, 0, 1),
        datetime(2026, 9, 24, 11, 59, 59),
        datetime(2026, 9, 24, 12, 0, 0),
        datetime(2026, 9, 24, 12, 0, 1),
        datetime(2026, 9, 24, 23, 59, 59),
    ],
)
def test_round_trip_boundary_values(adapter: DigitalClockAdapter, value: datetime) -> None:
    adapter.set_date_time(value)

    assert adapter.get_date_time() == value


def test_round_trip_every_second_of_day(adapter: DigitalClockAdapter) -> None:
    start = datetime(2026, 9, 24)

    for offset in range(24 * 60 * 60):
        value = start + timedelta(seconds=offset)
        adapter.set_date_time(value)
        assert adapter.get_date_time() == value


@pytest.mark.parametrize(
    "value",
    [
        datetime(2024, 2, 29, 10, 0, 0),
        datetime(2026, 12, 31, 23, 59, 59),
        datetime(2027, 1, 1, 0, 0, 0),
    ],
)
def test_date_is_passed_unchanged(
    adapter: DigitalClockAdapter, analog: AnalogClock, value: datetime
) -> None:
    adapter.set_date_time(value)

    assert (analog.get_year(), analog.get_month(), analog.get_day()) == (
        value.year,
        value.month,
        value.day,
    )
    assert adapter.get_date_time() == value


def test_microseconds_are_dropped(adapter: DigitalClockAdapter) -> None:
    adapter.set_date_time(datetime(2026, 9, 24, 12, 0, 0, 123456))

    assert adapter.get_date_time() == datetime(2026, 9, 24, 12, 0, 0)


def test_adapter_is_digital_clock(adapter: DigitalClockAdapter) -> None:
    assert isinstance(adapter, BaseDigitalClock)


def test_adapter_works_with_digital_client(adapter: DigitalClockAdapter) -> None:
    adapter.set_date_time(datetime(2026, 9, 24, 18, 5, 9))

    assert DigitalClockDisplay(adapter).render() == "2026-09-24 18:05:09"
