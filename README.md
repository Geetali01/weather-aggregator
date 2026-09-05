# Weather Aggregator

A weather aggregation service built with hexagonal (ports & adapters) architecture,
following a full TDD/BDD workflow. Fetches current conditions for a city from
Open-Meteo, stores them, and serves history through a REST API and a small React UI.

## Architecture

- **`domain/`** — pure business logic. `WeatherReading` (the core model),
  `WeatherService` (the use case), `WeatherProviderPort` and `WeatherRepositoryPort`
  (interfaces), and domain exceptions. Zero framework, HTTP, or DB imports.
- **`adapters/outbound/`** — implementations of the ports:
  `OpenMeteoAdapter` (real HTTP calls to Open-Meteo) and
  `SqliteWeatherRepository` (real SQLite persistence).
- **`adapters/inbound/rest/`** — FastAPI routes translating HTTP <-> domain calls.
- **`main.py`** — the composition root; the only place that wires concrete
  adapters into the domain service.
- **`frontend/`** — a small React (Vite) UI: enter a city, fetch its weather,
  see stored readings.

The domain never imports FastAPI, `requests`, or `sqlite3` directly — it only
depends on the abstract ports, which is what let the whole service be unit
tested with fakes before any adapter existed.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm

## Running the backend
python -m venv venv
venv\Scripts\activate # Windows
pip install -r requirements.txt
uvicorn main:app --reload

API docs: http://127.0.0.1:8000/docs

## Running the frontend
cd frontend
npm install
npm run dev

UI: http://localhost:5173

## Running the tests

All backend suites (from the project root, with `venv` active):
pytest tests/unit -v # domain logic, mocked ports
pytest tests/integration -v # real SQLite
pytest tests/component -v # full app, stubbed Open-Meteo
pytest tests/contract -v # Pact consumer + provider verification
behave # BDD scenarios

Or all pytest suites at once: `pytest`

Frontend tests:
cd frontend
npm test

## Design decisions

- **`requests` over `httpx`** for the HTTP adapter, so the `responses` library
  could cleanly stub calls in component tests without extra shims.
- **Plain `sqlite3`, no ORM** — keeps the repository adapter simple and its
  SQL explicit for a service this size.
- **Manual dependency injection** (`main.py`'s `create_app` factory) rather
  than a DI framework, since FastAPI's own `Depends` system would have coupled
  the domain more tightly to the web framework.
- **BDD steps reuse the component-test setup** (in-memory SQLite + stubbed
  Open-Meteo) rather than spinning up separate infrastructure, per the brief.

## CI

`.github/workflows/ci.yml` runs the full backend and frontend test suites onevery push to `main`.