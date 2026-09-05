"""Domain-level exceptions. These cross port boundaries but stay framework-free."""


class CityNotFoundError(Exception):
    """Raised when the geocoding provider has no match for a city name."""

    def __init__(self, city: str):
        self.city = city
        super().__init__(f"City not found: {city}")


class WeatherProviderError(Exception):
    """Raised when the external weather provider fails or returns bad data."""

    def __init__(self, message: str, cause: Exception | None = None):
        self.cause = cause
        super().__init__(message)