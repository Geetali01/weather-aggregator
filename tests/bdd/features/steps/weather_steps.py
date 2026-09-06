# pyright: reportMissingTypeStubs=false, reportAttributeAccessIssue=false, reportUnknownVariableType=false, reportUntypedFunctionDecorator=false
"""
Step definitions connecting the Gherkin scenarios in weather.feature
to the running FastAPI app, reusing the same stub-based setup as
the component tests via context (see environment.py).
"""
from __future__ import annotations

from typing import Any

from behave import given, when, then

from adapters.outbound.open_meteo_adapter import GEOCODING_URL, FORECAST_URL


def _stub_city(
    context: Any,
    city: str,
    lat: float = 45.75,
    lon: float = 21.23,
    country: str = "Romania",
    temperature: float = 22.4,
    windspeed: float = 14.2,
    weathercode: int = 3,
) -> None:
    context.responses.add(
        "GET", GEOCODING_URL,
        json={"results": [{"latitude": lat, "longitude": lon, "name": city, "country": country}]},
        status=200,
    )
    context.responses.add(
        "GET", FORECAST_URL,
        json={"current_weather": {"temperature": temperature, "windspeed": windspeed,
                                   "weathercode": weathercode, "time": "2024-06-01T14:00"}},
        status=200,
    )


@given("the weather aggregator app is running with a stubbed weather provider")
def step_app_running(context: Any) -> None:
    assert context.client is not None


@given('Open-Meteo has current weather data for "{city}"')
def step_open_meteo_has_data(context: Any, city: str) -> None:
    _stub_city(context, city)


@given('Open-Meteo has no data for "{city}"')
def step_open_meteo_has_no_data(context: Any, city: str) -> None:
    context.responses.add("GET", GEOCODING_URL, json={"results": []}, status=200)


@given('I have already fetched the weather for "{city}" once')
def step_fetch_once(context: Any, city: str) -> None:
    response = context.client.post("/weather/fetch", params={"city": city})
    assert response.status_code == 200


@when('I request the current weather for "{city}"')
def step_request_weather(context: Any, city: str) -> None:
    context.last_response = context.client.post("/weather/fetch", params={"city": city})


@when('I request the current weather for "{city}" again')
def step_request_weather_again(context: Any, city: str) -> None:
    context.last_response = context.client.post("/weather/fetch", params={"city": city})


@when('I view the weather history for "{city}"')
def step_view_history(context: Any, city: str) -> None:
    context.last_response = context.client.get(f"/weather/{city}")


@then("the response should be successful")
def step_response_successful(context: Any) -> None:
    assert context.last_response.status_code == 200


@then('the stored reading should show the city "{city}"')
def step_stored_reading_city(context: Any, city: str) -> None:
    body = context.last_response.json()
    assert body["city"] == city


@then("the history should contain {count:d} readings")
def step_history_count(context: Any, count: int) -> None:
    body = context.last_response.json()
    assert len(body) == count


@then("the response should indicate the city was not found")
def step_city_not_found(context: Any) -> None:
    assert context.last_response.status_code == 404