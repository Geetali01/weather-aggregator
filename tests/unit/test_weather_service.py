from datetime import datetime, timezone

import pytest

from domain.exceptions import CityNotFoundError, WeatherProviderError
from domain.models import WeatherReading
from domain.ports import WeatherProviderPort, WeatherRepositoryPort
from domain.services import WeatherService


class FakeProvider(WeatherProviderPort):
    """Test double standing in for the real weather API adapter."""

    def __init__(self, reading: WeatherReading | None = None, error: Exception | None = None):
        self._reading = reading
        self._error = error
        self.requested_city = None

    def get_current_weather(self, city: str) -> WeatherReading:
        self.requested_city = city
        if self._error:
            raise self._error
        return self._reading


class FakeRepository(WeatherRepositoryPort):
    """Test double standing in for the real database adapter."""

    def __init__(self):
        self._store = []
        self._next_id = 1

    def save(self, reading: WeatherReading) -> WeatherReading:
        saved = reading.with_id(self._next_id)
        self._next_id += 1
        self._store.append(saved)
        return saved

    def find_by_city(self, city: str) -> list[WeatherReading]:
        matches = [r for r in self._store if r.city == city]
        return sorted(matches, key=lambda r: r.observed_at, reverse=True)

    def find_latest_by_city(self, city: str):
        matches = self.find_by_city(city)
        return matches[0] if matches else None


def make_reading(city="Timisoara") -> WeatherReading:
    return WeatherReading(
        city=city,
        temperature_c=22.4,
        wind_speed_kmh=14.2,
        description="Overcast",
        observed_at=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc),
    )


def test_successful_fetch_and_store_returns_saved_reading_with_id():
    provider = FakeProvider(reading=make_reading())
    repository = FakeRepository()
    service = WeatherService(provider, repository)

    result = service.fetch_and_store("Timisoara")

    assert provider.requested_city == "Timisoara"
    assert result.id == 1
    assert result.city == "Timisoara"


def test_external_api_failure_propagates_and_stores_nothing():
    provider = FakeProvider(error=WeatherProviderError("Open-Meteo is down"))
    repository = FakeRepository()
    service = WeatherService(provider, repository)

    with pytest.raises(WeatherProviderError):
        service.fetch_and_store("Timisoara")

    assert repository.find_by_city("Timisoara") == []


def test_city_not_found_propagates_and_stores_nothing():
    provider = FakeProvider(error=CityNotFoundError("Atlantis"))
    repository = FakeRepository()
    service = WeatherService(provider, repository)

    with pytest.raises(CityNotFoundError):
        service.fetch_and_store("Atlantis")

    assert repository.find_by_city("Atlantis") == []