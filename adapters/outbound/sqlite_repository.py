"""
Outbound adapter implementing WeatherRepositoryPort against SQLite.
Uses the stdlib sqlite3 module directly — no ORM.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

from domain.models import WeatherReading
from domain.ports import WeatherRepositoryPort

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    wind_speed_kmh REAL NOT NULL,
    description TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
"""


def _row_to_reading(row: sqlite3.Row) -> WeatherReading:
    return WeatherReading(
        id=row["id"],
        city=row["city"],
        temperature_c=row["temperature_c"],
        wind_speed_kmh=row["wind_speed_kmh"],
        description=row["description"],
        observed_at=datetime.fromisoformat(row["observed_at"]),
        fetched_at=datetime.fromisoformat(row["fetched_at"]),
    )


class SqliteWeatherRepository(WeatherRepositoryPort):
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def save(self, reading: WeatherReading) -> WeatherReading:
        cursor = self._conn.execute(
            """
            INSERT INTO weather_readings
                (city, temperature_c, wind_speed_kmh, description, observed_at, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                reading.city,
                reading.temperature_c,
                reading.wind_speed_kmh,
                reading.description,
                reading.observed_at.isoformat(),
                reading.fetched_at.isoformat(),
            ),
        )
        self._conn.commit()
        assert cursor.lastrowid is not None
        return reading.with_id(cursor.lastrowid)

    def find_by_city(self, city: str) -> list[WeatherReading]:
        rows = self._conn.execute(
            "SELECT * FROM weather_readings WHERE city = ? ORDER BY observed_at DESC, id DESC",
            (city,),
        ).fetchall()
        return [_row_to_reading(row) for row in rows]

    def find_latest_by_city(self, city: str) -> WeatherReading | None:
        row = self._conn.execute(
            "SELECT * FROM weather_readings WHERE city = ? ORDER BY observed_at DESC, id DESC LIMIT 1",
            (city,),
        ).fetchone()
        return _row_to_reading(row) if row else None

    def close(self) -> None:
        self._conn.close()