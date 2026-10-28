from dataclasses import dataclass
from datetime import date
from typing import Any

@dataclass
class DailyForecast:
    date: date
    weather_code: int | None
    uv_index_max: float | None
    wind_speed_10m_max: float | None
    temperature_2m_max: float | None
    temperature_2m_min: float | None
    moon_phase: float | None

@dataclass
class WeatherForecast:
    latitude: float
    longitude: float
    timezone: str
    daily_units: dict[str, str]
    days: list[DailyForecast]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "WeatherForecast":
        daily = data["daily"]
        dates = daily["time"]

        def get_value(values: list, index: int):
            return values[index] if index < len(values) else None

        days = [
            DailyForecast(
                date=date.fromisoformat(day),
                weather_code=get_value(daily.get("weather_code", []), i),
                uv_index_max=get_value(daily.get("uv_index_max", []), i),
                wind_speed_10m_max=get_value(
                    daily.get("wind_speed_10m_max", []), i
                ),
                temperature_2m_max=get_value(
                    daily.get("temperature_2m_max", []), i
                ),
                temperature_2m_min=get_value(
                    daily.get("temperature_2m_min", []), i
                ),
                moon_phase=get_value(daily.get("moon_phase", []), i),
            )
            for i, day in enumerate(dates)
        ]

        return cls(
            latitude=data["latitude"],
            longitude=data["longitude"],
            timezone=data["timezone"],
            daily_units=data.get("daily_units", {}),
            days=days,
        )