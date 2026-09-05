"""
Composition root — the only place that knows about both adapters
and the domain. Wires concrete adapters into the ports.
"""
from __future__ import annotations

import os

from fastapi import FastAPI

from adapters.inbound.rest import api as rest_api
from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from domain.services import WeatherService


def create_app(provider=None, repository=None) -> FastAPI:
    """Factory so tests can inject stub/fake adapters."""
    provider = provider or OpenMeteoAdapter()
    db_path = os.environ.get("WEATHER_DB_PATH", "weather.db")
    repository = repository or SqliteWeatherRepository(db_path)

    rest_api.weather_service = WeatherService(provider, repository)

    app = FastAPI(title="Weather Aggregator")
    app.include_router(rest_api.router)
    return app


app = create_app()