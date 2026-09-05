from behave import given, when, then

from adapters.outbound.open_meteo_adapter import GEOCODING_URL, FORECAST_URL


def _stub_city(context, city, lat=45.75, lon=21.23, country="Romania",
                temperature=22.4, windspeed=14.2, weathercode=3):
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
def step_app_running(context):
    assert context.client is not None


@given('Open-Meteo has current weather data for "{city}"')
def step_open_meteo_has_data(context, city):
    _stub_city(context, city)


@given('Open-Meteo has no data for "{city}"')
def step_open_meteo_has_no_data(context, city):
    context.responses.add("GET", GEOCODING_URL, json={"results": []}, status=200)


@given('I have already fetched the weather for "{city}" once')
def step_fetch_once(context, city):
    response = context.client.post("/weather/fetch", params={"city": city})
    assert response.status_code == 200


@when('I request the current weather for "{city}"')
def step_request_weather(context, city):
    context.last_response = context.client.post("/weather/fetch", params={"city": city})


@when('I request the current weather for "{city}" again')
def step_request_weather_again(context, city):
    context.last_response = context.client.post("/weather/fetch", params={"city": city})


@when('I view the weather history for "{city}"')
def step_view_history(context, city):
    context.last_response = context.client.get(f"/weather/{city}")


@then("the response should be successful")
def step_response_successful(context):
    assert context.last_response.status_code == 200


@then('the stored reading should show the city "{city}"')
def step_stored_reading_city(context, city):
    body = context.last_response.json()
    assert body["city"] == city


@then("the history should contain {count:d} readings")
def step_history_count(context, count):
    body = context.last_response.json()
    assert len(body) == count


@then("the response should indicate the city was not found")
def step_city_not_found(context):
    assert context.last_response.status_code == 404