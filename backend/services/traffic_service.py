"""
backend/services/traffic_service.py — Traffic Flow Aggregation & MongoDB Persistence Service.

Provides:
  - TomTom Flow Segment data collection with 5-minute in-memory TTL caching
  - Sampling of route polyline points to compute route-level congestion metrics
  - Persistence of flow records into MongoDB traffic_data collection
  - User-friendly calculations (currentSpeed, freeFlowSpeed, delay, roadStatus)
"""
from __future__ import annotations

import time
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from backend.repositories.traffic_repository import TrafficRepository
from backend.services.traffic_adapter import (
    TrafficProviderAdapter,
    TomTomTrafficAdapter,
    SimulatedTrafficAdapter,
)


class TrafficService:
    def __init__(
        self,
        traffic_repo: Optional[TrafficRepository] = None,
        provider: Optional[TrafficProviderAdapter] = None,
        cache_ttl_sec: int = 300,  # 5 minutes
    ):
        self.traffic_repo = traffic_repo or TrafficRepository()
        self.provider = provider or TomTomTrafficAdapter()
        self.fallback_provider = SimulatedTrafficAdapter()
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def get_flow_at_point(
        self, lat: float, lng: float, zoom: int = 10, persist: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch traffic flow segment data for a single geographic coordinate.
        Checks 5-minute memory cache, falls back to provider, and persists to MongoDB.
        """
        cache_key = f"{round(lat, 4)}_{round(lng, 4)}_{zoom}"
        now_ts = time.time()

        # 1. Check in-memory cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if now_ts - cached_time < self.cache_ttl_sec:
                logger.debug(f"Returning cached traffic for ({lat}, {lng})")
                return cached_data

        # 2. Query provider (TomTom -> Fallback)
        flow = self.provider.get_flow_segment(lat, lng, zoom)
        if not flow:
            flow = self.fallback_provider.get_flow_segment(lat, lng, zoom)

        # 3. Compute derived traffic delay and congestion status
        curr_speed = flow.get("currentSpeed", 40.0)
        ff_speed = max(flow.get("freeFlowSpeed", 50.0), 1.0)
        curr_time = flow.get("currentTravelTime", 60)
        ff_time = flow.get("freeFlowTravelTime", 45)

        delay_sec = max(curr_time - ff_time, 0)
        speed_ratio = curr_speed / ff_speed

        if flow.get("roadClosure", False):
            status = "ROAD_CLOSED"
            congestion_level = "High"
        elif speed_ratio >= 0.80:
            status = "FREE_FLOW"
            congestion_level = "Low"
        elif speed_ratio >= 0.50:
            status = "MODERATE_TRAFFIC"
            congestion_level = "Medium"
        else:
            status = "HEAVY_CONGESTION"
            congestion_level = "High"

        result = {
            "latitude": lat,
            "longitude": lng,
            "currentSpeed": round(curr_speed, 1),
            "freeFlowSpeed": round(ff_speed, 1),
            "currentTravelTime": curr_time,
            "freeFlowTravelTime": ff_time,
            "delaySeconds": delay_sec,
            "delayMinutes": round(delay_sec / 60.0, 1),
            "speedRatio": round(speed_ratio, 2),
            "congestionLevel": congestion_level,
            "roadStatus": status,
            "confidence": flow.get("confidence", 0.9),
            "roadClosure": flow.get("roadClosure", False),
            "source": flow.get("source", "tomtom"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 4. Save to in-memory cache
        self._cache[cache_key] = (now_ts, result)

        # 5. Persist to MongoDB traffic_data collection
        if persist:
            try:
                segment_hash = f"seg_{abs(int(lat*10000))}_{abs(int(lng*10000))}"
                self.traffic_repo.create({
                    "segment_id": segment_hash,
                    "road_id": f"Road-Point-({lat:.3f},{lng:.3f})",
                    "timestamp": datetime.now(timezone.utc),
                    "speed_kmh": curr_speed,
                    "free_flow_speed": ff_speed,
                    "current_travel_time": curr_time,
                    "free_flow_travel_time": ff_time,
                    "confidence": flow.get("confidence", 0.9),
                    "road_closure": flow.get("roadClosure", False),
                    "lat": lat,
                    "lng": lng,
                    "source": flow.get("source", "tomtom"),
                })
            except Exception as e:
                logger.warning(f"Failed to persist traffic record to MongoDB: {e}")

        return result

    def get_route_traffic_flow(
        self, coordinates: List[List[float]], num_samples: int = 5
    ) -> Dict[str, Any]:
        """
        Sample multiple points along a route's polyline to calculate composite traffic metrics.
        """
        if not coordinates or len(coordinates) == 0:
            return {
                "averageCurrentSpeed": 42.0,
                "averageFreeFlowSpeed": 50.0,
                "totalDelayMinutes": 2.5,
                "congestionLevel": "Low",
                "roadStatus": "FREE_FLOW",
                "sampledSegments": [],
            }

        # Sample equidistant points
        total_pts = len(coordinates)
        sample_indices = []
        if total_pts <= num_samples:
            sample_indices = list(range(total_pts))
        else:
            step = (total_pts - 1) / (num_samples - 1)
            sample_indices = [int(round(i * step)) for i in range(num_samples)]

        segments = []
        total_curr_speed = 0.0
        total_ff_speed = 0.0
        total_delay = 0

        for idx in sample_indices:
            pt = coordinates[idx]
            lat, lng = pt[0], pt[1]
            seg_data = self.get_flow_at_point(lat, lng, persist=True)
            segments.append(seg_data)
            total_curr_speed += seg_data["currentSpeed"]
            total_ff_speed += seg_data["freeFlowSpeed"]
            total_delay += seg_data["delaySeconds"]

        count = len(segments)
        avg_curr_speed = round(total_curr_speed / count, 1)
        avg_ff_speed = round(total_ff_speed / count, 1)
        speed_ratio = avg_curr_speed / max(avg_ff_speed, 1.0)

        if speed_ratio >= 0.80:
            overall_status = "FREE_FLOW"
            overall_congestion = "Low"
        elif speed_ratio >= 0.50:
            overall_status = "MODERATE_TRAFFIC"
            overall_congestion = "Medium"
        else:
            overall_status = "HEAVY_CONGESTION"
            overall_congestion = "High"

        return {
            "averageCurrentSpeed": avg_curr_speed,
            "averageFreeFlowSpeed": avg_ff_speed,
            "totalDelaySeconds": total_delay,
            "totalDelayMinutes": round(total_delay / 60.0, 1),
            "speedRatio": round(speed_ratio, 2),
            "congestionLevel": overall_congestion,
            "roadStatus": overall_status,
            "sampledSegmentsCount": count,
            "sampledSegments": segments,
        }
