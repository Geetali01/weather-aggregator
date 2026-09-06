"""
Inbound adapter: translates HTTP requests into calls on WeatherService
and domain results/errors into HTTP responses.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from domain.exceptions import CityNotFoundError, WeatherProviderError
from domain.models import WeatherReading
from domain.services import WeatherService

router = APIRouter()

# Set by main.py at startup — simple manual dependency injection.
weather_service: WeatherService | None = None


def _reading_to_dict(reading: WeatherReading) -> dict[str, Any]:
    return {
        "id": reading.id,
        "city": reading.city,
        "temperature_c": reading.temperature_c,
        "wind_speed_kmh": reading.wind_speed_kmh,
        "description": reading.description,
        "observed_at": reading.observed_at.isoformat(),
        "fetched_at": reading.fetched_at.isoformat(),
    }


@router.post("/weather/fetch")
def fetch_weather(city: str) -> dict[str, Any]:
    assert weather_service is not None, "weather_service not wired"
    try:
        reading = weather_service.fetch_and_store(city)
    except CityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WeatherProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _reading_to_dict(reading)


@router.get("/weather/{city}")
def get_history(city: str) -> list[dict[str, Any]]:
    assert weather_service is not None, "weather_service not wired"
    readings = weather_service.get_history(city)
    return [_reading_to_dict(r) for r in readings]


@router.get("/weather/{city}/latest")
def get_latest(city: str) -> dict[str, Any]:
    assert weather_service is not None, "weather_service not wired"
    reading = weather_service.get_latest(city)
    if reading is None:
        raise HTTPException(status_code=404, detail=f"No readings stored for '{city}'")
    return _reading_to_dict(reading)