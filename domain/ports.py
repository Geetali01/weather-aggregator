"""
Ports: abstract boundaries the domain talks to.

The domain only ever imports these interfaces. Concrete adapters
(HTTP client, database, etc.) live outside the domain and implement them.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from domain.models import WeatherReading


class WeatherProviderPort(ABC):
    """Outbound port: fetch current weather for a city from an external source."""

    @abstractmethod
    def get_current_weather(self, city: str) -> WeatherReading:
        """
        Resolve `city` and fetch its current conditions.

        Raises:
            CityNotFoundError: if the city cannot be resolved.
            WeatherProviderError: if the external call fails or is malformed.
        """
        raise NotImplementedError


class WeatherRepositoryPort(ABC):
    """Outbound port: persist and query stored weather readings."""

    @abstractmethod
    def save(self, reading: WeatherReading) -> WeatherReading:
        """Persist a reading and return it with its assigned id."""
        raise NotImplementedError

    @abstractmethod
    def find_by_city(self, city: str) -> list[WeatherReading]:
        """Return all readings for a city, most recent first."""
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_city(self, city: str) -> WeatherReading | None:
        """Return the single most recent reading for a city, or None."""
        raise NotImplementedError


class WeatherCachePort(ABC):
    """Outbound port: a fast, ephemeral store checked before hitting the real provider."""

    @abstractmethod
    def get(self, city: str) -> WeatherReading | None:
        """Return a cached reading for city, or None if not cached / expired."""
        raise NotImplementedError

    @abstractmethod
    def set(self, city: str, reading: WeatherReading) -> None:
        """Cache a reading for city."""
        raise NotImplementedError