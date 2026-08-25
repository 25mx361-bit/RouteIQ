"""
backend/routes/weather_routes.py — Open-Meteo Weather Endpoints.

Endpoints:
  GET /api/weather/current   — Current atmospheric telemetry & risk score
  GET /api/weather/forecast  — Target travel datetime weather forecast & risk score
"""
from __future__ import annotations

from flask import Blueprint
from backend.controllers.weather_controller import get_current, get_forecast

weather_routes_bp = Blueprint("weather_routes", __name__)

weather_routes_bp.get("/current")(get_current)
weather_routes_bp.get("/forecast")(get_forecast)
