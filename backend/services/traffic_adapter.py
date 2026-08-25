"""
backend/services/traffic_adapter.py — Traffic Provider Adapter Interface & TomTom Implementation.

Allows swapping traffic data providers (TomTom, HERE, Google, Simulation) cleanly.
Uses the EXACT TomTom Flow Segment Data API response structure.
"""
from __future__ import annotations

import abc
import os
import time
import random
from typing import Any, Dict, List, Optional
import requests
from loguru import logger

from backend.config.settings import get_config


class TrafficProviderAdapter(abc.ABC):
    """Abstract interface for external traffic data providers."""

    @abc.abstractmethod
    def get_flow_segment(
        self, lat: float, lng: float, zoom: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch flow segment data for coordinates.
        Returns dictionary conforming to the standard flow segment schema.
        """
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        pass


class TomTomTrafficAdapter(TrafficProviderAdapter):
    """
    TomTom Traffic Flow API implementation using the Flow Segment Data endpoint.
    Endpoint: https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/{zoom}/json
    """

    BASE_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute"

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        cfg = get_config()
        self.api_key = api_key or cfg.TOMTOM_API_KEY or os.getenv("TOMTOM_API_KEY", "")
        self.max_retries = max_retries

    def get_provider_name(self) -> str:
        return "tomtom"

    def get_flow_segment(
        self, lat: float, lng: float, zoom: int = 10
    ) -> Optional[Dict[str, Any]]:
        if not self.api_key or self.api_key in ("your-tomtom-api-key-here", "placeholder", ""):
            logger.debug("TomTom API key not set; falling back to simulated provider.")
            return None

        url = f"{self.BASE_URL}/{zoom}/json"
        params = {
            "point": f"{lat},{lng}",
            "unit": "KMPH",
            "key": self.api_key,
        }

        # Exponential backoff retry loop
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"TomTom Flow API request (attempt {attempt}): point=({lat}, {lng})")
                resp = requests.get(url, params=params, timeout=5)

                if resp.status_code == 200:
                    data = resp.json()
                    # Actual TomTom Flow Segment Response structure
                    flow_data = data.get("flowSegmentData", {})
                    if flow_data:
                        return {
                            "frc": flow_data.get("frc", "FRC1"),
                            "currentSpeed": float(flow_data.get("currentSpeed", 0.0)),
                            "freeFlowSpeed": float(flow_data.get("freeFlowSpeed", 0.0)),
                            "currentTravelTime": int(flow_data.get("currentTravelTime", 0)),
                            "freeFlowTravelTime": int(flow_data.get("freeFlowTravelTime", 0)),
                            "confidence": float(flow_data.get("confidence", 1.0)),
                            "roadClosure": bool(flow_data.get("roadClosure", False)),
                            "coordinates": flow_data.get("coordinates", {}),
                            "source": "tomtom",
                            "raw": flow_data,
                        }
                    return None

                elif resp.status_code == 429:
                    logger.warning(f"TomTom API rate limit (429) hit on attempt {attempt}.")
                    if attempt < self.max_retries:
                        backoff = (2 ** attempt) * 0.5 + random.uniform(0.1, 0.3)
                        time.sleep(backoff)
                        continue
                    return None

                else:
                    logger.warning(f"TomTom API error HTTP {resp.status_code}: {resp.text[:150]}")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"TomTom API timeout on attempt {attempt}")
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)
            except Exception as e:
                logger.error(f"TomTom API request exception: {e}")
                break

        return None


class SimulatedTrafficAdapter(TrafficProviderAdapter):
    """
    High-fidelity fallback adapter matching the EXACT TomTom API flowSegmentData structure.
    Simulates realistic urban traffic patterns based on Coimbatore road hierarchy and time of day.
    """

    def get_provider_name(self) -> str:
        return "tomtom_simulated"

    def get_flow_segment(
        self, lat: float, lng: float, zoom: int = 10
    ) -> Optional[Dict[str, Any]]:
        # Compute baseline speed from road coordinate hash
        seed = int(abs(lat * 1000 + lng * 1000)) % 100
        free_flow_speed = 50.0 + (seed % 20)  # 50 - 70 km/h

        # Peak hours simulation (08:00-10:30 and 17:00-20:30)
        now_hour = time.localtime().tm_hour
        is_peak = (8 <= now_hour <= 10) or (17 <= now_hour <= 20)

        if is_peak:
            speed_factor = 0.55 + ((seed % 25) / 100.0)  # 55% - 80% speed
        else:
            speed_factor = 0.85 + ((seed % 15) / 100.0)  # 85% - 100% speed

        current_speed = round(free_flow_speed * speed_factor, 1)

        # Baseline distance for segment ~ 500m
        distance_m = 500.0
        free_flow_travel_time = int((distance_m / (free_flow_speed * 1000 / 3600)))
        current_travel_time = int((distance_m / (max(current_speed, 1.0) * 1000 / 3600)))

        return {
            "frc": "FRC2",
            "currentSpeed": current_speed,
            "freeFlowSpeed": free_flow_speed,
            "currentTravelTime": current_travel_time,
            "freeFlowTravelTime": free_flow_travel_time,
            "confidence": 0.92,
            "roadClosure": False,
            "coordinates": {
                "coordinate": [
                    {"latitude": lat, "longitude": lng},
                    {"latitude": lat + 0.002, "longitude": lng + 0.002},
                ]
            },
            "source": "tomtom_simulated",
            "raw": {},
        }
