
## SEE : https://api.open-meteo.com/v1/forecast?latitude=47.15498&longitude=2.18232&daily=weather_code,uv_index_max,wind_speed_10m_max,temperature_2m_max,temperature_2m_min,moon_phase&timezone=Europe%2FBerlin&forecast_days=3

import requests

from ..models.dataClasses_ApiMeteo import WeatherForecast

DEFAULT_LATITUDE    = 47.15498
DEFAULT_LONGITUDE   = 2.18232

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={DEFAULT_LATITUDE}"
    f"&longitude={DEFAULT_LONGITUDE}"
    "&daily=weather_code,uv_index_max,wind_speed_10m_max,"
    "temperature_2m_max,temperature_2m_min,moon_phase"
    "&timezone=Europe%2FBerlin"
    "&forecast_days=3"
)

response = requests.get(url, timeout=10)
response.raise_for_status()

forecast = WeatherForecast.from_json(response.json())

for day in forecast.days:
    print(
        day.date,
        day.temperature_2m_min,
        day.temperature_2m_max,
        day.weather_code,
        day.moon_phase,
    )