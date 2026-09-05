from domain.weather_codes import describe_weather_code


def test_known_code_maps_to_readable_description():
    assert describe_weather_code(3) == "Overcast"
    assert describe_weather_code(0) == "Clear sky"
    assert describe_weather_code(61) == "Rain: slight"


def test_unknown_code_returns_a_fallback_string():
    assert "Unknown" in describe_weather_code(9999)