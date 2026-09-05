from datetime import datetime, timezone

from adapters.outbound.console_notifier import ConsoleNotifier
from domain.models import WeatherReading


def make_reading(city="Timisoara") -> WeatherReading:
    return WeatherReading(
        city=city,
        temperature_c=22.4,
        wind_speed_kmh=14.2,
        description="Overcast",
        observed_at=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc),
    )


def test_notify_prints_the_city_and_temperature(capsys):
    notifier = ConsoleNotifier()

    notifier.notify(make_reading())

    captured = capsys.readouterr()
    assert "Timisoara" in captured.out
    assert "22.4" in captured.out