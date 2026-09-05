"""
Outbound adapter implementing WeatherProviderPort against Open-Meteo.
This is the only place that knows Open-Meteo's URLs and JSON shape.
"""
from __future__ import annotations

from datetime import datetime, timezone

import requests

from domain.exceptions import CityNotFoundError, WeatherProviderError
from domain.models import WeatherReading
from domain.ports import WeatherProviderPort
from domain.weather_codes import describe_weather_code

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoAdapter(WeatherProviderPort):
    def __init__(self, session: requests.Session | None = None, timeout: float = 5.0):
        # Accepting a session lets tests inject one pointed at a stub server.
        self._session = session or requests.Session()
        self._timeout = timeout

    def get_current_weather(self, city: str) -> WeatherReading:
        lat, lon, resolved_name = self._geocode(city)
        return self._fetch_current(resolved_name, lat, lon)

    def _geocode(self, city: str) -> tuple[float, float, str]:
        try:
            response = self._session.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise WeatherProviderError(f"Geocoding request failed for '{city}'", exc) from exc

        results = payload.get("results")
        if not results:
            raise CityNotFoundError(city)

        first = results[0]
        try:
            return float(first["latitude"]), float(first["longitude"]), first["name"]
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherProviderError(f"Malformed geocoding response for '{city}'", exc) from exc

    def _fetch_current(self, resolved_name: str, lat: float, lon: float) -> WeatherReading:
        try:
            response = self._session.get(
                FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": "true",
                    "wind_speed_unit": "kmh",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise WeatherProviderError(f"Forecast request failed for '{resolved_name}'", exc) from exc

        try:
            current = payload["current_weather"]
            observed_at = datetime.fromisoformat(current["time"]).replace(tzinfo=timezone.utc)
            return WeatherReading(
                city=resolved_name,
                temperature_c=float(current["temperature"]),
                wind_speed_kmh=float(current["windspeed"]),
                description=describe_weather_code(int(current["weathercode"])),
                observed_at=observed_at,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise WeatherProviderError(f"Malformed forecast response for '{resolved_name}'", exc) from exc