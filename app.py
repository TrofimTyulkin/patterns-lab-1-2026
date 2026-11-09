from datetime import datetime

from facades.clock_facade import ClockFacade


def main() -> None:
    clock = ClockFacade()

    for value in (
        datetime(2026, 11, 9, 0, 0, 0),
        datetime(2026, 11, 9, 12, 0, 0),
        datetime(2026, 11, 9, 23, 59, 59),
        datetime.now(),
    ):
        clock.set_date_time(value)

    print("Текущее время:", clock.get_date_time())
    print("Форматированное:", clock.get_formatted())
    print("Свой формат:", clock.get_formatted("%H:%M:%S %d.%m.%Y"))

    print("История изменений:")
    for item in clock.get_history():
        print(" ", item)


if __name__ == "__main__":
    main()
