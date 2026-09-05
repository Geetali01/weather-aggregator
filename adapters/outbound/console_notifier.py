"""
Outbound adapter implementing NotifierPort by logging to the console.
Swappable for email, Slack, or a webhook without touching the domain,
since WeatherService only depends on NotifierPort.
"""
from __future__ import annotations

from domain.models import WeatherReading
from domain.ports import NotifierPort


class ConsoleNotifier(NotifierPort):
    def notify(self, reading: WeatherReading) -> None:
        print(
            f"[notification] New reading for {reading.city}: "
            f"{reading.temperature_c}°C, {reading.description}"
        )