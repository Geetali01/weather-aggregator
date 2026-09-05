"""
Application service. Orchestrates the ports. Zero framework, HTTP,
or DB imports here — this is what unit tests exercise with mocks/stubs.
"""
from __future__ import annotations

from domain.models import WeatherReading
from domain.ports import WeatherCachePort, WeatherProviderPort, WeatherRepositoryPort


class WeatherService:
    def __init__(
        self,
        provider: WeatherProviderPort,
        repository: WeatherRepositoryPort,
        cache: WeatherCachePort | None = None,
        notifier=None,
    ):
        self._provider = provider
        self._repository = repository
        self._cache = cache
        self._notifier = notifier

    def fetch_and_store(self, city: str) -> WeatherReading:
        if self._cache is not None:
            cached = self._cache.get(city)
            if cached is not None:
                return cached

        reading = self._provider.get_current_weather(city)
        saved = self._repository.save(reading)

        if self._cache is not None:
            self._cache.set(city, saved)

        if self._notifier is not None:
            self._notifier.notify(saved)

        return saved

    def get_history(self, city: str) -> list[WeatherReading]:
        return self._repository.find_by_city(city)

    def get_latest(self, city: str) -> WeatherReading | None:
        return self._repository.find_latest_by_city(city)