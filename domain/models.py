"""Pure domain models. No framework, HTTP, or DB dependencies allowed here."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class WeatherReading:
    """A single weather observation for a city, ready to persist or return."""
    city: str
    temperature_c: float
    wind_speed_kmh: float
    description: str
    observed_at: datetime
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None

    def with_id(self, new_id: int) -> "WeatherReading":
        return WeatherReading(
            id=new_id,
            city=self.city,
            temperature_c=self.temperature_c,
            wind_speed_kmh=self.wind_speed_kmh,
            description=self.description,
            observed_at=self.observed_at,
            fetched_at=self.fetched_at,
        )