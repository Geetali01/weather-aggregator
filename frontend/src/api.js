const API_BASE_URL = "http://localhost:8000";

export async function fetchWeather(city) {
  const response = await fetch(
    `${API_BASE_URL}/weather/fetch?city=${encodeURIComponent(city)}`,
    { method: "POST" }
  );
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchHistory(city) {
  const response = await fetch(`${API_BASE_URL}/weather/${encodeURIComponent(city)}`);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}
export async function fetchLatest(city) {
  const response = await fetch(`${API_BASE_URL}/weather/${encodeURIComponent(city)}/latest`);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
}