"""
backend/services/weather_risk_calculator.py — Single Reusable Weather Risk Assessment Engine.

Rule Specification & Risk Formula:
===================================
A single deterministic formula calculating driving safety risk score [0.0 - 1.0].

1. Precipitation / Rainfall Risk (max +0.50):
   - rain > 25.0 mm       -> +0.50 (Torrential rain / flash flood & aquaplaning risk)
   - 10.0 < rain <= 25.0  -> +0.35 (Heavy rain / slick roads & braking distance increase)
   - 2.5  < rain <= 10.0  -> +0.20 (Moderate rain)
   - 0.1  < rain <= 2.5   -> +0.05 (Light drizzle)

2. Visibility Risk (max +0.30):
   - visibility < 1000 m  -> +0.30 (Dense fog / near-zero visibility)
   - 1000 <= visibility < 3000 m -> +0.15 (Moderate fog / mist)
   - 3000 <= visibility < 6000 m -> +0.05 (Hazy / reduced sightlines)

3. Wind Speed Risk (max +0.25):
   - wind > 50.0 km/h     -> +0.25 (Gale / severe crosswinds affecting vehicle stability)
   - 35.0 < wind <= 50.0  -> +0.15 (High crosswinds)
   - 25.0 < wind <= 35.0  -> +0.05 (Moderate gusts)

4. Extreme Temperature Risk (max +0.10):
   - temp > 42.0°C (Extreme heat / tire degradation & overheating) or temp < 2.0°C (Frost risk): +0.10

Overall Score: Clamped to range [0.0, 1.0].
Risk Categories:
  - 0.00 - 0.25: Low (Safe driving conditions)
  - 0.26 - 0.50: Moderate (Exercise caution, wet roads)
  - 0.51 - 0.75: High (Adverse weather, speed reduction recommended)
  - 0.76 - 1.00: Severe (Hazardous driving conditions)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


def calculate_weather_risk(
    temperature: float = 28.0,
    precipitation: float = 0.0,
    visibility: float = 10000.0,
    wind_speed: float = 10.0,
    humidity: Optional[float] = None,
    surface_pressure: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate composite weather risk score based on atmospheric parameters.

    Returns:
        {
            "risk_score": float (0.0 to 1.0),
            "risk_level": "Low" | "Moderate" | "High" | "Severe",
            "is_hazardous": bool,
            "risk_factors": list[str],
            "recommendation": str,
        }
    """
    score = 0.0
    factors: List[str] = []

    # 1. Precipitation / Rainfall
    precip = max(float(precipitation or 0.0), 0.0)
    if precip > 25.0:
        score += 0.50
        factors.append(f"Torrential rainfall ({precip:.1f} mm)")
    elif precip > 10.0:
        score += 0.35
        factors.append(f"Heavy rainfall ({precip:.1f} mm)")
    elif precip > 2.5:
        score += 0.20
        factors.append(f"Moderate rain ({precip:.1f} mm)")
    elif precip > 0.1:
        score += 0.05
        factors.append(f"Light rain/drizzle ({precip:.1f} mm)")

    # 2. Visibility
    vis = max(float(visibility if visibility is not None else 10000.0), 0.0)
    if vis < 1000.0:
        score += 0.30
        factors.append(f"Dense fog / very low visibility ({vis:.0f} m)")
    elif vis < 3000.0:
        score += 0.15
        factors.append(f"Moderate fog/mist ({vis:.0f} m)")
    elif vis < 6000.0:
        score += 0.05
        factors.append(f"Reduced visibility ({vis:.0f} m)")

    # 3. Wind Speed
    wind = max(float(wind_speed or 0.0), 0.0)
    if wind > 50.0:
        score += 0.25
        factors.append(f"Severe gale crosswinds ({wind:.1f} km/h)")
    elif wind > 35.0:
        score += 0.15
        factors.append(f"Strong crosswinds ({wind:.1f} km/h)")
    elif wind > 25.0:
        score += 0.05
        factors.append(f"Breezy conditions ({wind:.1f} km/h)")

    # 4. Extreme Temperature
    temp = float(temperature if temperature is not None else 28.0)
    if temp > 42.0:
        score += 0.10
        factors.append(f"Extreme heat ({temp:.1f}°C)")
    elif temp < 2.0:
        score += 0.10
        factors.append(f"Freezing temperature hazard ({temp:.1f}°C)")

    # Clamp score
    final_score = min(max(round(score, 2), 0.0), 1.0)

    # Determine risk category
    if final_score > 0.75:
        risk_level = "Severe"
        recommendation = "Severe weather conditions. Travel not advised or expect extreme delays."
    elif final_score > 0.50:
        risk_level = "High"
        recommendation = "Adverse weather. Reduce driving speed, increase braking distance, and switch on headlights."
    elif final_score > 0.25:
        risk_level = "Moderate"
        recommendation = "Moderate weather impact. Exercise caution on wet road segments."
    else:
        risk_level = "Low"
        recommendation = "Favourable weather. Standard driving conditions."

    if not factors:
        factors.append("Optimal atmospheric conditions")

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "is_hazardous": final_score > 0.50,
        "risk_factors": factors,
        "recommendation": recommendation,
    }
