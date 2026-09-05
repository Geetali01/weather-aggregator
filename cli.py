"""
Inbound adapter: a command-line interface driving the exact same
WeatherService used by the REST API. Proves the domain doesn't care
how it's invoked — this and main.py both just call WeatherService.
"""
from __future__ import annotations

import argparse
import os

from adapters.outbound.console_notifier import ConsoleNotifier
from adapters.outbound.in_memory_cache import InMemoryCache
from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from domain.exceptions import CityNotFoundError, WeatherProviderError
from domain.services import WeatherService


def build_service() -> WeatherService:
    provider = OpenMeteoAdapter()
    db_path = os.environ.get("WEATHER_DB_PATH", "weather.db")
    repository = SqliteWeatherRepository(db_path)
    cache = InMemoryCache()
    notifier = ConsoleNotifier()
    return WeatherService(provider, repository, cache=cache, notifier=notifier)


def cmd_fetch(service: WeatherService, args) -> None:
    try:
        reading = service.fetch_and_store(args.city)
    except CityNotFoundError as exc:
        print(f"Error: {exc}")
        return
    except WeatherProviderError as exc:
        print(f"Error: {exc}")
        return

    print(f"{reading.city}: {reading.temperature_c}°C, {reading.description}")


def cmd_history(service: WeatherService, args) -> None:
    readings = service.get_history(args.city)
    if not readings:
        print(f"No readings stored for '{args.city}'")
        return
    for reading in readings:
        print(f"{reading.observed_at} — {reading.temperature_c}°C, {reading.description}")


def cmd_latest(service: WeatherService, args) -> None:
    reading = service.get_latest(args.city)
    if reading is None:
        print(f"No readings stored for '{args.city}'")
        return
    print(f"{reading.city}: {reading.temperature_c}°C, {reading.description}")


def main():
    parser = argparse.ArgumentParser(description="Weather Aggregator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch and store current weather for a city")
    fetch_parser.add_argument("city")
    fetch_parser.set_defaults(func=cmd_fetch)

    history_parser = subparsers.add_parser("history", help="Show all stored readings for a city")
    history_parser.add_argument("city")
    history_parser.set_defaults(func=cmd_history)

    latest_parser = subparsers.add_parser("latest", help="Show the latest reading for a city")
    latest_parser.add_argument("city")
    latest_parser.set_defaults(func=cmd_latest)

    args = parser.parse_args()
    service = build_service()
    args.func(service, args)


if __name__ == "__main__":
    main()