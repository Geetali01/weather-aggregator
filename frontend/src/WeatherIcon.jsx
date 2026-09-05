function iconFor(description = "") {
  const d = description.toLowerCase();
  if (d.includes("thunder")) return "bolt";
  if (d.includes("snow")) return "snow";
  if (d.includes("rain") || d.includes("drizzle")) return "rain";
  if (d.includes("fog")) return "fog";
  if (d.includes("clear") || d.includes("mainly clear")) return "sun";
  return "cloud";
}

export default function WeatherIcon({ description, size = 40 }) {
  const kind = iconFor(description);
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.4,
    strokeLinecap: "round",
    strokeLinejoin: "round",
  };

  if (kind === "sun") {
    return (
      <svg {...common} aria-hidden="true">
        <circle cx="12" cy="12" r="4.5" />
        <path d="M12 2.5v2.5M12 19v2.5M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2.5 12H5M19 12h2.5M4.2 19.8L6 18M18 6l1.8-1.8" />
      </svg>
    );
  }
  if (kind === "rain") {
    return (
      <svg {...common} aria-hidden="true">
        <path d="M7 15.5a4.5 4.5 0 0 1 .8-8.94 6 6 0 0 1 11.2 2.2A4 4 0 0 1 18 15.5H7Z" />
        <path d="M9 19l-1 2M13 19l-1 2M17 19l-1 2" />
      </svg>
    );
  }
  if (kind === "snow") {
    return (
      <svg {...common} aria-hidden="true">
        <path d="M7 15.5a4.5 4.5 0 0 1 .8-8.94 6 6 0 0 1 11.2 2.2A4 4 0 0 1 18 15.5H7Z" />
        <path d="M9 19v2M9 19l-1.2 1M9 19l1.2 1M14 19v2M14 19l-1.2 1M14 19l1.2 1" />
      </svg>
    );
  }
  if (kind === "bolt") {
    return (
      <svg {...common} aria-hidden="true">
        <path d="M7 15.5a4.5 4.5 0 0 1 .8-8.94 6 6 0 0 1 11.2 2.2A4 4 0 0 1 18 15.5H7Z" />
        <path d="M13 14l-3 4h2.5l-1.5 4 4-5h-2.5l1.5-3z" />
      </svg>
    );
  }
  if (kind === "fog") {
    return (
      <svg {...common} aria-hidden="true">
        <path d="M4 9.5h11M4 13h16M4 16.5h13" />
      </svg>
    );
  }
  return (
    <svg {...common} aria-hidden="true">
      <path d="M7 16a4.5 4.5 0 0 1 .8-8.94 6 6 0 0 1 11.2 2.2A4 4 0 0 1 18 16H7Z" />
    </svg>
  );
}