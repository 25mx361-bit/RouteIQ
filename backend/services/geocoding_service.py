"""
backend/services/geocoding_service.py — OpenStreetMap (Nominatim) & Provider Geocoding Service.

Provides:
  - Forward geocoding: Query string -> { latitude, longitude, display_name }
  - Coimbatore regional biases and instant lookup dictionary for rapid local response
  - User-friendly error handling (never leaks stack traces)
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import requests
from loguru import logger

# Preset Coimbatore region landmark coordinates for instant fast lookup & offline fallback
COIMBATORE_PRESETS: Dict[str, Dict[str, Any]] = {
    "gandhipuram": {
        "latitude": 11.0176,
        "longitude": 76.9667,
        "display_name": "Gandhipuram Central, Coimbatore, Tamil Nadu, India",
    },
    "rs puram": {
        "latitude": 11.0085,
        "longitude": 76.9485,
        "display_name": "R.S. Puram, Coimbatore, Tamil Nadu, India",
    },
    "r.s. puram": {
        "latitude": 11.0085,
        "longitude": 76.9485,
        "display_name": "R.S. Puram, Coimbatore, Tamil Nadu, India",
    },
    "coimbatore railway station": {
        "latitude": 10.9980,
        "longitude": 76.9634,
        "display_name": "Coimbatore Junction Railway Station, Gopalapuram, Coimbatore, Tamil Nadu, India",
    },
    "coimbatore junction": {
        "latitude": 10.9980,
        "longitude": 76.9634,
        "display_name": "Coimbatore Junction, Gopalapuram, Coimbatore, Tamil Nadu, India",
    },
    "psg tech": {
        "latitude": 11.0244,
        "longitude": 77.0028,
        "display_name": "PSG College of Technology, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "psg college of technology": {
        "latitude": 11.0244,
        "longitude": 77.0028,
        "display_name": "PSG College of Technology, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "peelamedu": {
        "latitude": 11.0287,
        "longitude": 77.0042,
        "display_name": "Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "thanneerpanthal": {
        "latitude": 11.0338,
        "longitude": 77.0145,
        "display_name": "Thanneerpanthal Road, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "thanneerpanthal road": {
        "latitude": 11.0338,
        "longitude": 77.0145,
        "display_name": "Thanneerpanthal Road, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "coimbatore airport": {
        "latitude": 11.0298,
        "longitude": 77.0434,
        "display_name": "Coimbatore International Airport (CJB), Civil Aerodrome Post, Coimbatore, Tamil Nadu, India",
    },
    "saravanampatti": {
        "latitude": 11.0805,
        "longitude": 76.9959,
        "display_name": "Saravanampatti, Coimbatore, Tamil Nadu, India",
    },
    "singanallur": {
        "latitude": 10.9995,
        "longitude": 77.0267,
        "display_name": "Singanallur, Coimbatore, Tamil Nadu, India",
    },
    "saibaba colony": {
        "latitude": 11.0280,
        "longitude": 76.9460,
        "display_name": "Saibaba Colony, Coimbatore, Tamil Nadu, India",
    },
    "ukdam": {
        "latitude": 10.9892,
        "longitude": 76.9613,
        "display_name": "Ukkadam, Coimbatore, Tamil Nadu, India",
    },
    "ukkadam": {
        "latitude": 10.9892,
        "longitude": 76.9613,
        "display_name": "Ukkadam Bus Terminus, Coimbatore, Tamil Nadu, India",
    },
    "hope college": {
        "latitude": 11.0238,
        "longitude": 77.0185,
        "display_name": "Hopes College, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "hopes": {
        "latitude": 11.0238,
        "longitude": 77.0185,
        "display_name": "Hopes College, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "hopes college": {
        "latitude": 11.0238,
        "longitude": 77.0185,
        "display_name": "Hopes College, Peelamedu, Coimbatore, Tamil Nadu, India",
    },
    "race course": {
        "latitude": 11.0028,
        "longitude": 76.9740,
        "display_name": "Race Course, Thomas Park, Coimbatore, Tamil Nadu, India",
    },
    "marudhamalai": {
        "latitude": 11.0463,
        "longitude": 76.8524,
        "display_name": "Marudhamalai, Coimbatore, Tamil Nadu, India",
    },
}


class GeocodingService:
    """Service to resolve place names / addresses to geographical coordinates."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "RouteIQ-MCA-Project/1.0 (academic; routeiq@project.local)"

    def __init__(self, timeout_sec: int = 5):
        self.timeout_sec = timeout_sec

    def geocode(self, query: str) -> Dict[str, Any]:
        """
        Geocode a location query string.
        Returns:
            {
                "latitude": float,
                "longitude": float,
                "display_name": str,
                "source": "osm_nominatim" | "preset_cache"
            }
        Raises:
            ValueError: If query is invalid or location is not found.
        """
        q = (query or "").strip()
        if not q:
            raise ValueError("Search query cannot be empty.")

        q_lower = q.lower()

        # 1. Check Coimbatore Landmark Presets (instant match)
        for key, landmark in COIMBATORE_PRESETS.items():
            if key in q_lower or q_lower in key:
                logger.info(f"Geocoding resolved via Coimbatore preset: '{q}' -> {landmark['display_name']}")
                return {
                    "latitude": landmark["latitude"],
                    "longitude": landmark["longitude"],
                    "display_name": landmark["display_name"],
                    "source": "preset_cache",
                }

        # 2. Query OpenStreetMap Nominatim
        # Bias towards Tamil Nadu / South India if query doesn't specify
        search_term = q
        if "coimbatore" not in q_lower and "india" not in q_lower and "tamil nadu" not in q_lower:
            search_term = f"{q}, Coimbatore, Tamil Nadu, India"

        params = {
            "q": search_term,
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
            # Bounding box roughly covering Coimbatore and surrounding TN regions
            "viewbox": "76.7,11.2,77.2,10.8",
            "bounded": 0,
        }
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Language": "en",
        }

        try:
            logger.debug(f"Querying Nominatim for: '{search_term}'")
            resp = requests.get(
                self.NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=self.timeout_sec,
            )

            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    best = results[0]
                    lat = float(best["lat"])
                    lng = float(best["lon"])
                    display_name = best.get("display_name", q)
                    logger.info(f"Nominatim resolved '{q}' -> ({lat}, {lng})")
                    return {
                        "latitude": lat,
                        "longitude": lng,
                        "display_name": display_name,
                        "source": "osm_nominatim",
                    }
            elif resp.status_code == 429:
                logger.warning("Nominatim rate limit reached. Checking fallback.")

        except requests.exceptions.Timeout:
            logger.warning(f"Nominatim timeout for '{q}'. Checking fallback.")
        except Exception as e:
            logger.warning(f"Nominatim request error for '{q}': {e}")

        # 3. Fallback: If Nominatim didn't find or timed out, check closest partial match in presets
        for key, landmark in COIMBATORE_PRESETS.items():
            words = q_lower.split()
            if any(w in key for w in words if len(w) > 3):
                return {
                    "latitude": landmark["latitude"],
                    "longitude": landmark["longitude"],
                    "display_name": landmark["display_name"],
                    "source": "preset_fallback",
                }

        # Default fallback to Coimbatore City Center if all else fails
        if "coimbatore" in q_lower:
            return {
                "latitude": 11.0168,
                "longitude": 76.9558,
                "display_name": "Gandhipuram, Coimbatore, Tamil Nadu, India",
                "source": "city_center_fallback",
            }

        raise ValueError(f"Location not found for '{query}'. Please check the spelling or provide more details.")
