import { useState } from "react";
import { fetchWeather, fetchHistory } from "./api";

function App() {
  const [city, setCity] = useState("");
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleFetchWeather(event) {
    event.preventDefault();
    if (!city.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const stored = await fetchWeather(city);
      const history = await fetchHistory(stored.city);
      setReadings(history);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Weather Aggregator</h1>

      <form onSubmit={handleFetchWeather}>
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter a city"
          aria-label="City"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Fetching..." : "Fetch Weather"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>Stored Readings</h2>
      {readings.length === 0 ? (
        <p>No readings yet. Fetch a city above.</p>
      ) : (
        <ul>
          {readings.map((reading) => (
            <li key={reading.id}>
              {reading.city}: {reading.temperature_c}°C, {reading.wind_speed_kmh} km/h,{" "}
              {reading.description} (observed {reading.observed_at})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;