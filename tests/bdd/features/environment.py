"""
Behave environment hooks: set up a fresh app + stubbed Open-Meteo
before each scenario, reusing the same TestClient/responses approach
as the component tests — no separate infrastructure spun up here.
"""
from __future__ import annotations

from typing import Any

import responses as responses_lib
from fastapi.testclient import TestClient

from adapters.outbound.in_memory_cache import InMemoryCache
from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from main import create_app


def before_scenario(context: Any, scenario: Any) -> None:
    context.responses = responses_lib.RequestsMock()
    context.responses.start()
    context.repository = SqliteWeatherRepository(":memory:")
    context.provider = OpenMeteoAdapter()
    # ttl_seconds=0 disables caching for these scenarios so we can test
    # the fetch -> store -> history flow without cache hits interfering.
    context.cache = InMemoryCache(ttl_seconds=0)
    context.app = create_app(
        provider=context.provider, repository=context.repository, cache=context.cache
    )
    context.client = TestClient(context.app)


def after_scenario(context: Any, scenario: Any) -> None:
    context.responses.stop()
    context.responses.reset()
    context.repository.close()