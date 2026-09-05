"""
Consumer-driven contract test for OpenMeteoAdapter.
Defines what we expect Open-Meteo's response shape to look like,
runs the real adapter against a local Pact mock server, and
writes out a Pact file describing that contract.
"""
import atexit
import os

import pytest
from pact import Consumer, Provider

from adapters.outbound.open_meteo_adapter import OpenMeteoAdapter

PACT_DIR = os.path.join(os.path.dirname(__file__), "pacts")
os.makedirs(PACT_DIR, exist_ok=True)

pact = Consumer("WeatherAggregatorService").has_pact_with(
    Provider("OpenMeteoAPI"),
    pact_dir=PACT_DIR,
    port=1234,
)
pact.start_service()
atexit.register(pact.stop_service)


@pytest.fixture
def adapter():
    import adapters.outbound.open_meteo_adapter as module

    original_geocoding = module.GEOCODING_URL
    original_forecast = module.FORECAST_URL
    module.GEOCODING_URL = f"{pact.uri}/v1/search"
    module.FORECAST_URL = f"{pact.uri}/v1/forecast"
    yield OpenMeteoAdapter()
    module.GEOCODING_URL = original_geocoding
    module.FORECAST_URL = original_forecast


def test_get_current_weather_matches_expected_open_meteo_contract(adapter):
    expected_geocoding_response = {
        "results": [
            {"latitude": 45.75, "longitude": 21.23, "name": "Timisoara", "country": "Romania"}
        ]
    }
    expected_forecast_response = {
        "current_weather": {
            "temperature": 22.4,
            "windspeed": 14.2,
            "weathercode": 3,
            "time": "2024-06-01T14:00",
        }
    }

    (
        pact.given("a city named Timisoara exists")
        .upon_receiving("a request to geocode Timisoara")
        .with_request(
            method="GET", path="/v1/search",
            query={"name": "Timisoara", "count": "1", "language": "en", "format": "json"},
        )
        .will_respond_with(200, body=expected_geocoding_response)
    )
    (
        pact.given("coordinates 45.75,21.23 have current weather data")
        .upon_receiving("a request for current weather at those coordinates")
        .with_request(
            method="GET", path="/v1/forecast",
            query={"latitude": "45.75", "longitude": "21.23",
                   "current_weather": "true", "wind_speed_unit": "kmh"},
        )
        .will_respond_with(200, body=expected_forecast_response)
    )

    with pact:
        reading = adapter.get_current_weather("Timisoara")

        assert reading.city == "Timisoara"
        assert reading.temperature_c == 22.4
        assert reading.description == "Overcast"
        