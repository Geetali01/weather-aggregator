"""
Outbound adapter implementing WeatherCachePort as a simple in-memory cache
with time-based expiry. Swappable for Redis or similar without touching
the domain, since WeatherService only depends on WeatherCachePort.
"""
from __future__ import annotations

import time

from domain.models import WeatherReading
from domain.ports import WeatherCachePort


class InMemoryCache(WeatherCachePort):
    def __init__(self, ttl_seconds: float = 300):
        self._ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, WeatherReading]] = {}

    def get(self, city: str) -> WeatherReading | None:
        entry = self._store.get(city)
        if entry is None:
            return None

        cached_at, reading = entry
        if time.time() - cached_at > self._ttl_seconds:
            del self._store[city]
            return None

        return reading

    def set(self, city: str, reading: WeatherReading) -> None:
        self._store[city] = (time.time(), reading)