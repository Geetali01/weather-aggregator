import { useState } from "react";
import { fetchWeather, fetchHistory, fetchLatest } from "./api";
import WeatherIcon from "./WeatherIcon";
import "./App.css";

function formatObservedAt(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatTime(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function Temperature({ value, size }) {
  return (
    <span style={{ fontSize: size }}>
      {value}
      <sup>°C</sup>
    </span>
  );
}

function App() {
  const [city, setCity] = useState("");
  const [lastFetchedCity, setLastFetchedCity] = useState(null);
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFullHistory, setShowFullHistory] = useState(false);

  async function loadReadings(resolvedCity, fullHistory) {
    if (fullHistory) {
      const history = await fetchHistory(resolvedCity);
      setReadings(history);
    } else {
      const latest = await fetchLatest(resolvedCity);
      setReadings([latest]);
    }
  }

  async function handleFetchWeather(event) {
    event.preventDefault();
    if (!city.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const stored = await fetchWeather(city);
      setLastFetchedCity(stored.city);
      await loadReadings(stored.city, showFullHistory);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleHistory(event) {
    const checked = event.target.checked;
    setShowFullHistory(checked);
    if (!lastFetchedCity) return;

    setLoading(true);
    setError(null);
    try {
      await loadReadings(lastFetchedCity, checked);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const [primary, ...rest] = readings;

  return (
    <div className="app">
      <p className="app__eyebrow">Current conditions, tracked over time</p>
      <h1 className="app__title">Weather Aggregator</h1>

      <form className="search" onSubmit={handleFetchWeather}>
        <input
          className="search__input"
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter a city, e.g. London"
          aria-label="City"
        />
        <button className="search__button" type="submit" disabled={loading}>
          {loading ? "Fetching…" : "Fetch weather"}
        </button>
      </form>

      <label className="toggle">
        <span className="toggle__switch">
          <input
            type="checkbox"
            checked={showFullHistory}
            onChange={handleToggleHistory}
          />
          <span className="toggle__track">
            <span className="toggle__thumb" />
          </span>
        </span>
        Show full history
      </label>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {readings.length === 0 ? (
        <div className="empty-state">No readings yet — fetch a city above.</div>
      ) : !showFullHistory ? (
        <div className="hero">
          <div className="hero__inner">
            <div className="hero__top">
              <WeatherIcon description={primary.description} />
              <span className="hero__city">{primary.city}</span>
            </div>
            <p className="hero__temp">
              <Temperature value={primary.temperature_c} size={76} />
            </p>
            <p className="hero__desc">
              {primary.description} · {primary.wind_speed_kmh} km/h wind
            </p>
            <p className="hero__meta">Observed {formatObservedAt(primary.observed_at)}</p>
          </div>
        </div>
      ) : (
        <>
          <p className="section-label">Stored readings</p>
          <ul className="timeline">
            {readings.map((reading) => (
              <li className="timeline-item" key={reading.id}>
                <div className="timeline-item__row">
                  <span className="timeline-item__temp">
                    <Temperature value={reading.temperature_c} size={20} />
                  </span>
                  <span className="timeline-item__desc">{reading.description}</span>
                </div>
                <p className="timeline-item__meta">
                  {formatTime(reading.observed_at)} · {reading.wind_speed_kmh} km/h
                </p>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;