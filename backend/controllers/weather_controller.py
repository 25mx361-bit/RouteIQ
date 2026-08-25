"""
backend/controllers/weather_controller.py — Weather API Controller.

Handles HTTP request validation and invokes WeatherService.
"""
from __future__ import annotations

from flask import request, jsonify
from loguru import logger
from backend.services.weather_service import WeatherService

weather_service = WeatherService()


def get_current():
    """
    Handle GET /api/weather/current?lat=...&lng=...
    """
    try:
        lat = float(request.args.get("lat", ""))
        lng = float(request.args.get("lng", ""))
    except (ValueError, TypeError):
        return jsonify({
            "error": "validation_error",
            "message": "'lat' and 'lng' query parameters must be valid numbers.",
        }), 422

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
        return jsonify({
            "error": "validation_error",
            "message": "Latitude or Longitude out of valid geographic range.",
        }), 422

    try:
        data = weather_service.get_current_weather(lat=lat, lng=lng)
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Weather query failed for ({lat}, {lng}): {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to fetch current weather data.",
        }), 500


def get_forecast():
    """
    Handle GET /api/weather/forecast?lat=...&lng=...&date=YYYY-MM-DD&time=HH:MM
    """
    try:
        lat = float(request.args.get("lat", ""))
        lng = float(request.args.get("lng", ""))
    except (ValueError, TypeError):
        return jsonify({
            "error": "validation_error",
            "message": "'lat' and 'lng' query parameters must be valid numbers.",
        }), 422

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
        return jsonify({
            "error": "validation_error",
            "message": "Latitude or Longitude out of valid geographic range.",
        }), 422

    date = request.args.get("date", "").strip()
    time = request.args.get("time", "").strip()

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not time:
        time = "12:00"

    try:
        data = weather_service.get_forecast_weather(
            lat=lat, lng=lng, date=date, time=time
        )
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Weather forecast query failed for ({lat}, {lng}) on {date} {time}: {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to fetch weather forecast.",
        }), 500
