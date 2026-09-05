"""
Composition root. This is the only place that knows about *both* adapters
and the domain — it wires concrete adapters into the ports and starts FastAPI.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.inbound.rest import api as rest_api
from adapters.outbound.in_memory_cache import InMemoryCache
from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from domain.services import WeatherService


def create_app(provider=None, repository=None, cache=None) -> FastAPI:
    """Factory so tests can inject stub/fake adapters instead of real ones."""
    provider = provider or OpenMeteoAdapter()
    db_path = os.environ.get("WEATHER_DB_PATH", "weather.db")
    repository = repository or SqliteWeatherRepository(db_path)
    cache = cache if cache is not None else InMemoryCache()

    rest_api.weather_service = WeatherService(provider, repository, cache=cache)

    app = FastAPI(title="Weather Aggregator")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(rest_api.router)
    return app


app = create_app()