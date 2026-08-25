"""
backend/services/weather_service.py — Open-Meteo Weather Service.

Provides:
  1. get_current_weather(lat, lng) — Real-time atmospheric conditions
  2. get_forecast_weather(lat, lng, date, time) — Travel-time future weather forecast
  3. get_historical_weather(lat, lng, start_date, end_date) — Archive data for ML training
  4. MongoDB snapshot persistence in weather_data collection
  5. Integration with weather_risk_calculator
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import requests
from loguru import logger

from backend.repositories.weather_repository import WeatherRepository
from backend.services.weather_risk_calculator import calculate_weather_risk

# WMO Weather Code Mappings
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherService:
    FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(
        self,
        weather_repo: Optional[WeatherRepository] = None,
        timeout_sec: int = 6,
    ):
        self.weather_repo = weather_repo or WeatherRepository()
        self.timeout_sec = timeout_sec

    def get_current_weather(
        self, lat: float, lng: float, persist: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch current atmospheric parameters from Open-Meteo Current endpoint.
        """
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,surface_pressure,wind_speed_10m",
            "hourly": "visibility",
            "timezone": "auto",
        }

        try:
            logger.debug(f"Querying Open-Meteo Current Weather for ({lat}, {lng})")
            resp = requests.get(self.FORECAST_API_URL, params=params, timeout=self.timeout_sec)
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current", {})
            temp = float(current.get("temperature_2m", 28.5))
            precip = float(current.get("precipitation", 0.0))
            humidity = float(current.get("relative_humidity_2m", 65.0))
            wind = float(current.get("wind_speed_10m", 12.0))
            pressure = float(current.get("surface_pressure", 1012.0))
            wcode = int(current.get("weather_code", 0))

            # Approximate visibility from hourly if present
            hourly_vis = data.get("hourly", {}).get("visibility", [])
            visibility = float(hourly_vis[0]) if hourly_vis else 10000.0

            condition = WMO_WEATHER_CODES.get(wcode, "Clear sky")
            source = "open_meteo"

        except Exception as e:
            logger.warning(f"Open-Meteo Current Weather request error ({e}). Using Coimbatore standard defaults.")
            temp = 29.0
            precip = 0.0
            humidity = 62.0
            wind = 11.5
            pressure = 1013.0
            visibility = 10000.0
            condition = "Partly cloudy"
            source = "coimbatore_fallback"

        # Calculate risk score
        risk = calculate_weather_risk(
            temperature=temp,
            precipitation=precip,
            visibility=visibility,
            wind_speed=wind,
            humidity=humidity,
            surface_pressure=pressure,
        )

        weather_snapshot = {
            "latitude": lat,
            "longitude": lng,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature_2m": temp,
            "precipitation": precip,
            "relative_humidity_2m": humidity,
            "wind_speed_10m": wind,
            "surface_pressure": pressure,
            "visibility": visibility,
            "condition": condition,
            "weather_risk": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "risk_factors": risk["risk_factors"],
            "recommendation": risk["recommendation"],
            "source": source,
        }

        if persist:
            self._persist_weather(lat, lng, weather_snapshot)

        return weather_snapshot

    def get_forecast_weather(
        self,
        lat: float,
        lng: float,
        date: str,
        time: str,
        persist: bool = True,
    ) -> Dict[str, Any]:
        """
        Fetch forecast atmospheric parameters for user's target travel datetime.
        """
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,weather_code,surface_pressure,wind_speed_10m,visibility",
            "timezone": "auto",
        }

        try:
            logger.debug(f"Querying Open-Meteo Forecast Weather for ({lat}, {lng}) on {date} {time}")
            resp = requests.get(self.FORECAST_API_URL, params=params, timeout=self.timeout_sec)
            resp.raise_for_status()
            data = resp.json()

            hourly = data.get("hourly", {})
            times = hourly.get("time", [])

            # Target datetime formatting
            time_clean = time if len(time) == 5 else f"{time[:2]}:00"
            target_str = f"{date}T{time_clean.split(':')[0]}:00"

            # Find matching or closest index
            match_idx = 0
            if target_str in times:
                match_idx = times.index(target_str)
            else:
                # Default to index nearest to target or first index
                match_idx = min(len(times) - 1, max(0, int(time_clean.split(':')[0])))

            temp = float(hourly.get("temperature_2m", [28.0])[match_idx])
            precip = float(hourly.get("precipitation", [0.0])[match_idx])
            humidity = float(hourly.get("relative_humidity_2m", [65.0])[match_idx])
            wind = float(hourly.get("wind_speed_10m", [12.0])[match_idx])
            pressure = float(hourly.get("surface_pressure", [1012.0])[match_idx])
            vis_list = hourly.get("visibility", [10000.0])
            visibility = float(vis_list[match_idx]) if match_idx < len(vis_list) else 10000.0
            wcode_list = hourly.get("weather_code", [0])
            wcode = int(wcode_list[match_idx]) if match_idx < len(wcode_list) else 0

            condition = WMO_WEATHER_CODES.get(wcode, "Clear sky")
            source = "open_meteo_forecast"

        except Exception as e:
            logger.warning(f"Open-Meteo Forecast Weather request error ({e}). Using Coimbatore forecast defaults.")
            temp = 28.0
            precip = 0.0
            humidity = 60.0
            wind = 10.0
            pressure = 1012.5
            visibility = 10000.0
            condition = "Mainly clear"
            source = "coimbatore_fallback"

        # Calculate risk score
        risk = calculate_weather_risk(
            temperature=temp,
            precipitation=precip,
            visibility=visibility,
            wind_speed=wind,
            humidity=humidity,
            surface_pressure=pressure,
        )

        forecast_snapshot = {
            "latitude": lat,
            "longitude": lng,
            "target_date": date,
            "target_time": time,
            "timestamp": f"{date}T{time}:00Z",
            "temperature_2m": temp,
            "precipitation": precip,
            "relative_humidity_2m": humidity,
            "wind_speed_10m": wind,
            "surface_pressure": pressure,
            "visibility": visibility,
            "condition": condition,
            "weather_risk": risk["risk_score"],
            "risk_level": risk["risk_level"],
            "risk_factors": risk["risk_factors"],
            "recommendation": risk["recommendation"],
            "source": source,
        }

        if persist:
            self._persist_weather(lat, lng, forecast_snapshot)

        return forecast_snapshot

    def get_historical_weather(
        self,
        lat: float,
        lng: float,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """
        Query Open-Meteo Historical Archive API for historical hourly atmospheric features.
        Used for ML training datasets (PatchTST and CatBoost pipelines).
        """
        params = {
            "latitude": lat,
            "longitude": lng,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,surface_pressure,wind_speed_10m",
            "timezone": "auto",
        }

        try:
            logger.info(f"Fetching historical weather for ({lat}, {lng}) between {start_date} and {end_date}")
            resp = requests.get(self.ARCHIVE_API_URL, params=params, timeout=12)
            resp.raise_for_status()
            data = resp.json()

            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            precips = hourly.get("precipitation", [])
            humidities = hourly.get("relative_humidity_2m", [])
            winds = hourly.get("wind_speed_10m", [])
            pressures = hourly.get("surface_pressure", [])

            records = []
            for i in range(len(times)):
                t_val = temps[i] if i < len(temps) else 28.0
                p_val = precips[i] if i < len(precips) else 0.0
                w_val = winds[i] if i < len(winds) else 10.0
                risk = calculate_weather_risk(temperature=t_val, precipitation=p_val, wind_speed=w_val)

                records.append({
                    "timestamp": times[i],
                    "latitude": lat,
                    "longitude": lng,
                    "temperature_2m": t_val,
                    "precipitation": p_val,
                    "relative_humidity_2m": humidities[i] if i < len(humidities) else 60.0,
                    "wind_speed_10m": w_val,
                    "surface_pressure": pressures[i] if i < len(pressures) else 1013.0,
                    "weather_risk": risk["risk_score"],
                })

            logger.info(f"Retrieved {len(records)} historical weather records from Open-Meteo Archive.")
            return records

        except Exception as e:
            logger.warning(f"Open-Meteo Archive API request failed: {e}")
            return []

    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------

    def _persist_weather(self, lat: float, lng: float, data: Dict[str, Any]):
        try:
            self.weather_repo.create({
                "timestamp": datetime.now(timezone.utc),
                "lat": lat,
                "lng": lng,
                "temperature": data.get("temperature_2m", 28.0),
                "rainfall_mm": data.get("precipitation", 0.0),
                "humidity_pct": data.get("relative_humidity_2m", 60.0),
                "wind_speed": data.get("wind_speed_10m", 10.0),
                "visibility_m": data.get("visibility", 10000.0),
                "condition": data.get("condition", "Clear sky"),
                "weather_risk": data.get("weather_risk", 0.0),
                "source": data.get("source", "open_meteo"),
            })
        except Exception as e:
            logger.warning(f"Notice: Failed to persist weather record to MongoDB: {e}")
