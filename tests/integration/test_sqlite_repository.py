import os
import uuid
from datetime import datetime, timezone

import pytest

from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from domain.models import WeatherReading


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / f"test-{uuid.uuid4().hex}.db"
    repo = SqliteWeatherRepository(str(db_path))
    yield repo
    repo.close()
    if os.path.exists(db_path):
        os.remove(db_path)


def make_reading(city="Timisoara", temp=22.4, when=None) -> WeatherReading:
    return WeatherReading(
        city=city,
        temperature_c=temp,
        wind_speed_kmh=14.2,
        description="Overcast",
        observed_at=when or datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc),
    )


def test_save_assigns_an_id(repository):
    saved = repository.save(make_reading())
    assert saved.id is not None
    assert saved.city == "Timisoara"


def test_find_by_city_returns_most_recent_first(repository):
    repository.save(make_reading(temp=10.0, when=datetime(2024, 6, 1, 8, 0, tzinfo=timezone.utc)))
    repository.save(make_reading(temp=22.4, when=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc)))
    repository.save(make_reading(city="Cluj", temp=5.0))

    results = repository.find_by_city("Timisoara")

    assert [r.temperature_c for r in results] == [22.4, 10.0]


def test_find_latest_by_city_returns_the_newest_reading(repository):
    repository.save(make_reading(temp=10.0, when=datetime(2024, 6, 1, 8, 0, tzinfo=timezone.utc)))
    repository.save(make_reading(temp=22.4, when=datetime(2024, 6, 1, 14, 0, tzinfo=timezone.utc)))

    assert repository.find_latest_by_city("Timisoara").temperature_c == 22.4


def test_find_latest_returns_none_when_nothing_stored(repository):
    assert repository.find_latest_by_city("Nowhere") is None