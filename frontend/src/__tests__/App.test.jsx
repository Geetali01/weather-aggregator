import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "../App";
import * as api from "../api";

describe("App", () => {
  it("fetches weather for a city and displays the latest reading", async () => {
    vi.spyOn(api, "fetchWeather").mockResolvedValue({ city: "London" });
    vi.spyOn(api, "fetchLatest").mockResolvedValue({
      id: 1,
      city: "London",
      temperature_c: 20.7,
      wind_speed_kmh: 9.4,
      description: "Partly cloudy",
      observed_at: "2026-09-05T12:45:00+00:00",
    });

    render(<App />);

    fireEvent.change(screen.getByLabelText("City"), { target: { value: "London" } });
    fireEvent.click(screen.getByText("Fetch weather"));

    await waitFor(() => {
      expect(screen.getByText("London")).toBeInTheDocument();
    });

    expect(screen.getByText("20.7")).toBeInTheDocument();
    expect(screen.getByText(/Partly cloudy/)).toBeInTheDocument();
    expect(api.fetchWeather).toHaveBeenCalledWith("London");
  });

  it("shows an error message when the fetch fails", async () => {
    vi.spyOn(api, "fetchWeather").mockRejectedValue(new Error("City not found: Atlantis"));

    render(<App />);

    fireEvent.change(screen.getByLabelText("City"), { target: { value: "Atlantis" } });
    fireEvent.click(screen.getByText("Fetch weather"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("City not found: Atlantis");
    });
  });
});