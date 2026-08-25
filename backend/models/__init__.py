"""
backend/models/__init__.py — Exports all 11 RouteIQ MongoDB models.
"""
from backend.models.base import BaseModel
from backend.models.user import UserModel
from backend.models.traffic_data import TrafficDataModel
from backend.models.weather_data import WeatherDataModel
from backend.models.routes import RouteModel
from backend.models.predictions import PredictionModel
from backend.models.events import EventModel
from backend.models.landslides import LandslideModel
from backend.models.notifications import NotificationModel
from backend.models.search_history import SearchHistoryModel
from backend.models.model_logs import ModelLogModel
from backend.models.system_logs import SystemLogModel

__all__ = [
    "BaseModel",
    "UserModel",
    "TrafficDataModel",
    "WeatherDataModel",
    "RouteModel",
    "PredictionModel",
    "EventModel",
    "LandslideModel",
    "NotificationModel",
    "SearchHistoryModel",
    "ModelLogModel",
    "SystemLogModel",
]
