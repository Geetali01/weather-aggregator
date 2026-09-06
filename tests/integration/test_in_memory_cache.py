from __future__ import annotations

import time
from datetime import datetime, timezone

from adapters.outbound.in_memory_cache import InMemoryCache
from domain.models import WeatherReading


def make_reading(city: str = "Timisoara") -> WeatherReading:
    return WeatherReading(
        city=city,
        temperature_c=22.4,
        wind_speed_kmh=14.2,
        description="Overcast",
        observed_at=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc),
    )


def test_set_then_get_returns_the_cached_reading() -> None:
    cache = InMemoryCache(ttl_seconds=60)
    cache.set("Timisoara", make_reading())

    result = cache.get("Timisoara")

    assert result is not None
    assert result.city == "Timisoara"


def test_get_returns_none_for_a_city_never_cached() -> None:
    cache = InMemoryCache(ttl_seconds=60)
    assert cache.get("Nowhere") is None


def test_entry_expires_after_the_ttl_elapses() -> None:
    cache = InMemoryCache(ttl_seconds=0.05)
    cache.set("Timisoara", make_reading())

    time.sleep(0.1)

    assert cache.get("Timisoara") is None