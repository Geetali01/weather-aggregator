"""
Outbound adapter implementing WeatherRepositoryPort against PostgreSQL.
Same interface as SqliteWeatherRepository — WeatherService, and therefore
the rest of the app, doesn't need to know or care which one is plugged in.
"""
from __future__ import annotations

from datetime import datetime

import psycopg2
import psycopg2.extras

from domain.models import WeatherReading
from domain.ports import WeatherRepositoryPort

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather_readings (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    wind_speed_kmh REAL NOT NULL,
    description TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL
);
"""


def _row_to_reading(row) -> WeatherReading:
    return WeatherReading(
        id=row["id"],
        city=row["city"],
        temperature_c=row["temperature_c"],
        wind_speed_kmh=row["wind_speed_kmh"],
        description=row["description"],
        observed_at=row["observed_at"],
        fetched_at=row["fetched_at"],
    )


class PostgresWeatherRepository(WeatherRepositoryPort):
    def __init__(self, dsn: str):
        self._conn = psycopg2.connect(dsn)
        self._conn.autocommit = True
        with self._conn.cursor() as cursor:
            cursor.execute(SCHEMA)

    def save(self, reading: WeatherReading) -> WeatherReading:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO weather_readings
                    (city, temperature_c, wind_speed_kmh, description, observed_at, fetched_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, city, temperature_c, wind_speed_kmh, description, observed_at, fetched_at
                """,
                (
                    reading.city,
                    reading.temperature_c,
                    reading.wind_speed_kmh,
                    reading.description,
                    reading.observed_at,
                    reading.fetched_at,
                ),
            )
            row = cursor.fetchone()
            return _row_to_reading(row)

    def find_by_city(self, city: str) -> list[WeatherReading]:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM weather_readings
                WHERE city = %s
                ORDER BY observed_at DESC, id DESC
                """,
                (city,),
            )
            rows = cursor.fetchall()
            return [_row_to_reading(row) for row in rows]

    def find_latest_by_city(self, city: str) -> WeatherReading | None:
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * FROM weather_readings
                WHERE city = %s
                ORDER BY observed_at DESC, id DESC
                LIMIT 1
                """,
                (city,),
            )
            row = cursor.fetchone()
            return _row_to_reading(row) if row else None

    def close(self) -> None:
        self._conn.close()