"""
Application service. Orchestrates the two ports. Zero framework, HTTP,
or DB imports here — this is what unit tests exercise with mocks/stubs.
"""
from __future__ import annotations

from domain.models import WeatherReading
from domain.ports import WeatherProviderPort, WeatherRepositoryPort


class WeatherService:
    def __init__(self, provider: WeatherProviderPort, repository: WeatherRepositoryPort):
        self._provider = provider
        self._repository = repository

    def fetch_and_store(self, city: str) -> WeatherReading:
        reading = self._provider.get_current_weather(city)
        return self._repository.save(reading)

    def get_history(self, city: str) -> list[WeatherReading]:
        return self._repository.find_by_city(city)

    def get_latest(self, city: str):
        return self._repository.find_latest_by_city(city)