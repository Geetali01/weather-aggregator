"""
Composition root. This is the only place that knows about *both* adapters
and the domain — it wires concrete adapters into the ports and starts FastAPI.
"""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.inbound.rest import api as rest_api
from adapters.outbound.console_notifier import ConsoleNotifier
from adapters.outbound.in_memory_cache import InMemoryCache
from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter
from adapters.outbound.postgres_repository import PostgresWeatherRepository
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from domain.ports import NotifierPort, WeatherCachePort, WeatherProviderPort, WeatherRepositoryPort
from domain.services import WeatherService


def _build_default_repository() -> WeatherRepositoryPort:
    """Pick the database adapter based on config, with no changes to the domain."""
    postgres_dsn = os.environ.get("WEATHER_POSTGRES_DSN")
    if postgres_dsn:
        return PostgresWeatherRepository(postgres_dsn)
    db_path = os.environ.get("WEATHER_DB_PATH", "weather.db")
    return SqliteWeatherRepository(db_path)


def create_app(
    provider: WeatherProviderPort | None = None,
    repository: WeatherRepositoryPort | None = None,
    cache: WeatherCachePort | None = None,
    notifier: NotifierPort | None = None,
) -> FastAPI:
    """Factory so tests can inject stub/fake adapters instead of real ones."""
    provider = provider or OpenMeteoAdapter()
    repository = repository or _build_default_repository()
    cache = cache if cache is not None else InMemoryCache()
    notifier = notifier if notifier is not None else ConsoleNotifier()

    rest_api.weather_service = WeatherService(provider, repository, cache=cache, notifier=notifier)

    app = FastAPI(title="Weather Aggregator")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(rest_api.router)
    return app


app = create_app()