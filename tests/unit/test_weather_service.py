from datetime import datetime, timezone

from domain.models import WeatherReading


def test_weather_reading_stores_the_fields_we_give_it():
    reading = WeatherReading(
        city="Timisoara",
        temperature_c=22.4,
        wind_speed_kmh=14.2,
        description="Overcast",
        observed_at=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc),
    )

    assert reading.city == "Timisoara"
    assert reading.temperature_c == 22.4
    assert reading.id is None