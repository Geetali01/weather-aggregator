# Weather Aggregator

A weather aggregation service built end to end using Hexagonal Architecture (Ports and Adapters), with full TDD/BDD test coverage. It fetches current weather conditions from a public external API, stores every reading, and exposes that data through a REST API, a command line interface, and a React web UI, all driving the exact same core business logic.

## 1. Project Overview

### 1.1 What the service does

- Fetches real, live current weather for any city from the Open-Meteo API, covering both geocoding and forecast lookups.
- Stores every reading it fetches, building a history over time.
- Exposes that data through a REST API built with FastAPI, a command line interface, and a React web UI.
- Supports two interchangeable databases, SQLite and PostgreSQL, switchable through a single environment variable with zero changes to business logic.
- Adds caching to avoid repeated calls to the weather API, and a notification hook that fires whenever a new reading is fetched.

## 2. Architecture: Hexagonal Ports and Adapters

The central idea of this architecture is that business logic, referred to as the domain, never depends on any specific framework, database, or HTTP library. The domain only depends on abstract interfaces called ports. Concrete implementations, called adapters, plug into those ports from the outside. Dependencies always point inward toward the domain, never outward.

### 2.1 Domain layer

Located in the `domain` folder. This is the center of the architecture and has zero external dependencies.

| File | Purpose |
|---|---|
| `models.py` | Defines `WeatherReading`, the core data shape. A pure dataclass with no framework code. |
| `ports.py` | Defines four abstract interfaces that the domain depends on. |
| `services.py` | Defines `WeatherService`, the actual use case logic covering fetch, store, cache, and notify. |
| `exceptions.py` | Defines `CityNotFoundError` and `WeatherProviderError`, the domain level errors. |
| `weather_codes.py` | A lookup table mapping Open-Meteo numeric weather codes to readable descriptions. |

### 2.2 The four ports

1. `WeatherProviderPort`, an outbound port meaning give me current weather for a city. Implemented by `OpenMeteoAdapter`.
2. `WeatherRepositoryPort`, an outbound port meaning save and query stored readings. Implemented by both `SqliteWeatherRepository` and `PostgresWeatherRepository`, which are fully interchangeable since they share the same interface and method signatures.
3. `WeatherCachePort`, an outbound port meaning check or store a short lived cached reading. Implemented by `InMemoryCache`.
4. `NotifierPort`, an outbound port meaning react whenever a new reading is fetched. Implemented by `ConsoleNotifier`.

The inbound side has no formal Python interface. `WeatherService`'s own public methods, namely `fetch_and_store`, `get_history`, and `get_latest`, serve as the inbound port. Two separate adapters call into it: the REST API and the command line interface.

### 2.3 Outbound adapters

Located in the `adapters/outbound` folder.

| Adapter | Implements | What it does |
|---|---|---|
| `open_meteo_adapter.py` | `WeatherProviderPort` | Makes real HTTP calls to Open-Meteo for geocoding and forecast data. |
| `sqlite_repository.py` | `WeatherRepositoryPort` | Persists readings to a SQLite file using the standard library `sqlite3` module, with no ORM. |
| `postgres_repository.py` | `WeatherRepositoryPort` | Same interface as SQLite, but persists to a real PostgreSQL database using `psycopg2`. |
| `in_memory_cache.py` | `WeatherCachePort` | An in process cache with a configurable time to live, defaulting to five minutes. |
| `console_notifier.py` | `NotifierPort` | Prints a notification line whenever a reading is fetched. |

### 2.4 Inbound adapters

| Adapter | File | What it does |
|---|---|---|
| REST API | `adapters/inbound/rest/api.py` | FastAPI routes: `POST /weather/fetch`, `GET /weather/{city}`, and `GET /weather/{city}/latest`. Translates HTTP requests into domain calls and domain exceptions into HTTP status codes. |
| Command line interface | `cli.py` | Supports `fetch`, `history`, and `latest` commands for a given city. Calls the exact same `WeatherService` as the REST API, proving the domain does not care how it is invoked. |

### 2.5 Composition root

`main.py` is the only file that imports both the concrete adapters and the domain. It selects SQLite or PostgreSQL based on the `WEATHER_POSTGRES_DSN` environment variable, wires the chosen provider, repository, cache, and notifier into `WeatherService`, and configures FastAPI with CORS enabled for the local frontend.

### 2.6 Frontend

A React application built with Vite, located in the `frontend` folder. It includes a city input with a fetch weather button, a toggle between showing the latest reading only or the full history, and a custom dark themed design using Fraunces for the featured temperature display and Inter for all other text. The frontend communicates with the backend purely over HTTP through `src/api.js`, with no backend internals leaking into the UI.

## 3. Testing: Six Layers, All Passing

The project follows a complete testing pyramid, covering every layer required for a production grade service.

| Layer | Location | What it proves |
|---|---|---|
| Unit tests | `tests/unit` | `WeatherService` tested in full isolation using `FakeProvider`, `FakeRepository`, `FakeCache`, and `FakeNotifier` test doubles. No real HTTP calls or database access. Written test driven, following a red then green cycle. |
| Integration tests | `tests/integration` | Each adapter tested against the real system it wraps: a real SQLite file, a real PostgreSQL database (automatically skipped if no test database is configured), the real in memory cache including actual time to live expiry, and the real console notifier's printed output. |
| Component tests | `tests/component` | The full FastAPI application started end to end, with only the external Open-Meteo API stubbed using the `responses` library. Proves that HTTP requests, domain logic, and database writes all work together correctly. |
| Contract tests using Pact | `tests/contract` | A consumer test defines exactly what the application expects Open-Meteo's responses to look like, running against a local Pact mock server and generating a contract file. A provider verification test then replays that contract against a stub server, proving the expectations can genuinely be satisfied. |
| BDD scenarios | `tests/bdd` | Plain English Given, When, Then scenarios written in Gherkin syntax inside `weather.feature`, wired to real step definitions that drive the same FastAPI application used in the component tests. |
| Frontend component tests | `frontend/src/__tests__` | The React UI tested in isolation using Vitest and React Testing Library, with the API layer mocked out. |

### 3.1 Running the tests

```
pytest              # runs unit, integration, component, and contract tests
behave              # runs the BDD scenarios
cd frontend && npm test   # runs the React test suite
```

## 4. Continuous Integration Pipeline

The file `.github/workflows/ci.yml` runs automatically on every push to the main branch, and consists of two jobs.

- The `backend-tests` job installs Python dependencies, then runs the unit, integration, component, and contract test suites, followed by the BDD scenarios, followed by a command line interface smoke test that fetches and reads back live weather for London against the real Open-Meteo API.
- The `frontend-tests` job installs npm dependencies and runs the Vitest suite.

Both jobs must pass for the overall pipeline to succeed.

## 5. Setup Instructions

### 5.1 Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer, with npm
- PostgreSQL 15 or newer, optional, only required to run in PostgreSQL mode

### 5.2 Backend setup

```
python -m venv venv
venv\Scripts\activate          (on Windows)
pip install -r requirements.txt
```

### 5.3 Frontend setup

```
cd frontend
npm install
```

### 5.4 PostgreSQL setup, optional

```
createdb weather_aggregator
```

or, from inside `psql`:

```
CREATE DATABASE weather_aggregator;
```

## 6. Running the Application

### 6.1 Backend in SQLite mode, the default, requiring no extra setup

```
uvicorn main:app --reload
```

### 6.2 Backend in PostgreSQL mode

```
set WEATHER_POSTGRES_DSN=postgresql://postgres:YOUR_PASSWORD@localhost:5432/weather_aggregator
uvicorn main:app --reload
```

### 6.3 Frontend

```
cd frontend
npm run dev
```

Then open the local address printed in the terminal, typically `http://localhost:5173`.

### 6.4 Command line interface

```
python cli.py fetch London
python cli.py history London
python cli.py latest London
```

### 6.5 Interactive API documentation

Visit `http://127.0.0.1:8000/docs` while the backend is running to see and try every endpoint.

## 7. Configuration Reference

| Environment variable | Purpose | Default |
|---|---|---|
| `WEATHER_DB_PATH` | Path to the SQLite database file | `weather.db` |
| `WEATHER_POSTGRES_DSN` | If set, switches the application to PostgreSQL instead of SQLite | unset, meaning SQLite is used |
| `WEATHER_TEST_POSTGRES_DSN` | If set, enables the PostgreSQL integration test suite | unset, meaning those tests are skipped |

## 8. Key Design Decisions

- The `requests` library was chosen over `httpx` for the HTTP adapter, so that the `responses` library could cleanly stub calls during component testing without extra workarounds.
- Plain `sqlite3` and `psycopg2` were used with no ORM, keeping each repository adapter's SQL explicit and easy to reason about at this project's scale.
- Manual dependency injection was used through `main.py`'s `create_app` factory function, instead of a dependency injection framework, so that the domain layer stays fully decoupled from FastAPI.
- The in memory cache uses a five minute time to live by default, balancing reduced load on the real weather API against how stale a cached reading is allowed to become. This value is configurable per instance.
- The BDD step definitions reuse the same component test setup, meaning an in memory SQLite database and a stubbed Open-Meteo API with caching disabled, rather than spinning up separate infrastructure. This keeps the test suite fast and self contained.
- The command line interface was deliberately built as a second inbound adapter to prove, not merely claim, that the hexagonal architecture works. The exact same `WeatherService`, cache, notifier, and repository are driven by a terminal command with zero changes to the domain layer.

## 9. Known Limitations and Possible Next Steps

- The cache is in process and in memory only. A shared cache across multiple running instances would require something like Redis.
- The API currently has no authentication or authorization.
- There is no rate limiting on calls to Open-Meteo beyond what the cache naturally provides.
- The PostgreSQL adapter currently opens one connection per repository instance rather than using a connection pool. This is acceptable at this scale, but a real connection pool, such as `psycopg2.pool`, would be needed for higher traffic.
