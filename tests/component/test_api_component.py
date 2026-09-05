"""
Component (service) tests: start the full FastAPI app with a real
SqliteWeatherRepository, but stub Open-Meteo with `responses`.
"""
import pytest
import responses
from fastapi.testclient import TestClient

from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter, GEOCODING_URL, FORECAST_URL
from adapters.outbound.sqlite_repository import SqliteWeatherRepository
from main import create_app


@pytest.fixture
def client():
    repository = SqliteWeatherRepository(":memory:")
    provider = OpenMeteoAdapter()
    app = create_app(provider=provider, repository=repository)
    with TestClient(app) as test_client:
        yield test_client
    repository.close()


def stub_open_meteo(city="Timisoara", country="Romania", lat=45.75, lon=21.23,
                     temperature=22.4, windspeed=14.2, weathercode=3):
    responses.add(
        responses.GET, GEOCODING_URL,
        json={"results": [{"latitude": lat, "longitude": lon, "name": city, "country": country}]},
        status=200,
    )
    responses.add(
        responses.GET, FORECAST_URL,
        json={"current_weather": {"temperature": temperature, "windspeed": windspeed,
                                   "weathercode": weathercode, "time": "2024-06-01T14:00"}},
        status=200,
    )


@responses.activate
def test_fetch_endpoint_stores_reading_and_returns_it(client):
    stub_open_meteo()
    response = client.post("/weather/fetch", params={"city": "Timisoara"})
    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Timisoara"
    assert body["temperature_c"] == 22.4
    assert body["description"] == "Overcast"


@responses.activate
def test_fetch_then_history_returns_stored_reading(client):
    stub_open_meteo()
    client.post("/weather/fetch", params={"city": "Timisoara"})
    response = client.get("/weather/Timisoara")
    assert response.status_code == 200
    assert len(response.json()) == 1


@responses.activate
def test_fetch_then_latest_returns_the_single_reading(client):
    stub_open_meteo()
    client.post("/weather/fetch", params={"city": "Timisoara"})
    response = client.get("/weather/Timisoara/latest")
    assert response.status_code == 200
    assert response.json()["city"] == "Timisoara"


def test_latest_returns_404_when_no_readings_stored(client):
    response = client.get("/weather/Nowhere/latest")
    assert response.status_code == 404


@responses.activate
def test_fetch_unknown_city_returns_404(client):
    responses.add(responses.GET, GEOCODING_URL, json={"results": []}, status=200)
    response = client.post("/weather/fetch", params={"city": "Atlantis"})
    assert response.status_code == 404


@responses.activate
def test_fetch_when_provider_errors_returns_502(client):
    responses.add(responses.GET, GEOCODING_URL, json={"error": "boom"}, status=500)
    response = client.post("/weather/fetch", params={"city": "Timisoara"})
    assert response.status_code == 502