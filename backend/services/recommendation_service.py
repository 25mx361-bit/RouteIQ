"""
backend/services/recommendation_service.py — Route recommendation with safety enforcement.

SAFETY RULES (enforced HERE — NOT inside CatBoost model):
─────────────────────────────────────────────────────────
Rule 1: If road_blocked == True  →  status = "BLOCKED", excluded from recommendation.
Rule 2: If landslide_active == True AND landslide_severity in {"HIGH", "CRITICAL"}
        →  status = "BLOCKED", excluded from recommendation.

These rules are applied BEFORE CatBoost scores are consulted.
A blocked route never appears as recommended regardless of its CatBoost score.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Severity levels that automatically block a route
_BLOCKING_SEVERITIES = {"HIGH", "CRITICAL"}


def apply_safety_filters(
    routes: List[Dict[str, Any]],
    feature_vectors: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Apply landslide and blockage safety rules to each route.

    Mutates route dicts in-place, adding/updating:
        is_blocked:      bool
        blocked_reason:  str | None
        catboost_eligible: bool (only eligible routes are scored)

    Args:
        routes:          List of route dicts (from routing service).
        feature_vectors: Corresponding feature vectors (same index order).

    Returns:
        Same list (mutated in-place) for chaining.
    """
    for route, fv in zip(routes, feature_vectors):
        road_blocked = bool(fv.get("road_blocked", 0))
        landslide_active = bool(fv.get("landslide_active", 0))
        landslide_severity = str(fv.get("landslide_severity", "NONE")).upper()

        # Rule 1 — Hard road blockage
        if road_blocked:
            route["is_blocked"] = True
            route["catboost_eligible"] = False
            route["blocked_reason"] = "Active road blockage detected on route corridor."
            continue

        # Rule 2 — High/Critical landslide proximate to route
        if landslide_active and landslide_severity in _BLOCKING_SEVERITIES:
            route["is_blocked"] = True
            route["catboost_eligible"] = False
            route["blocked_reason"] = (
                f"Active landslide with severity={landslide_severity} "
                "is within unsafe proximity of this route."
            )
            continue

        # Safe to recommend
        route["is_blocked"] = False
        route["catboost_eligible"] = True
        route["blocked_reason"] = None

    return routes


def rank_routes(
    routes: List[Dict[str, Any]],
    feature_vectors: List[Dict[str, Any]],
    use_catboost: bool = True,
) -> List[Dict[str, Any]]:
    """
    Full recommendation pipeline:
        1. Apply safety filters (BLOCKED routes are excluded immediately).
        2. Score eligible routes with CatBoost (if model exists).
        3. Rank by score descending; BLOCKED routes are appended at the end.
        4. Assign is_recommended=True to the highest-scoring non-blocked route.

    Args:
        routes:          Route dicts (from routing service / MongoDB).
        feature_vectors: Feature vectors in the same order as routes.
        use_catboost:    Set False to skip CatBoost (e.g., during tests).

    Returns:
        Ranked list of route dicts with added fields:
            catboost_score, catboost_label, is_recommended, rank.
    """
    if not routes:
        return []

    # Step 1: Safety enforcement
    apply_safety_filters(routes, feature_vectors)

    eligible_indices = [i for i, r in enumerate(routes) if r.get("catboost_eligible")]
    blocked_indices = [i for i, r in enumerate(routes) if not r.get("catboost_eligible")]

    # Step 2: Score eligible routes with CatBoost (if model exists)
    if use_catboost and eligible_indices:
        try:
            from ml.catboost.prediction import predict_route_scores
            eligible_fvs = [feature_vectors[i] for i in eligible_indices]
            scores = predict_route_scores(eligible_fvs)
            for score_result in scores:
                route_idx = eligible_indices[score_result["route_index"]]
                routes[route_idx]["raw_catboost_probability"] = score_result["score"]
                routes[route_idx]["catboost_label"] = score_result["label"]
        except FileNotFoundError:
            logger.warning("CatBoost model not found. Falling back to heuristic scoring.")
            use_catboost = False
        except Exception as exc:
            logger.error(f"CatBoost scoring failed: {exc}. Falling back to heuristic scoring.")
            use_catboost = False

    # Step 3: Compute intelligent composite suitability score for all eligible routes
    # Formula prioritizes Traffic (45%) and Travel Time (35%) over raw model probabilities
    all_durs = [float(routes[j].get("duration_min", feature_vectors[j].get("duration_min", 15.0))) for j in eligible_indices]
    min_dur = min(all_durs) if all_durs else 15.0
    max_dur = max(all_durs) if all_durs else 15.0
    dur_range = max_dur - min_dur

    all_dists = [float(routes[j].get("distance_km", feature_vectors[j].get("distance_km", 10.0))) for j in eligible_indices]
    min_dist = min(all_dists) if all_dists else 10.0
    max_dist = max(all_dists) if all_dists else 10.0
    dist_range = max_dist - min_dist

    for i in eligible_indices:
        fv = feature_vectors[i]
        r = routes[i]

        # 1. Traffic Congestion Score (TCI) — Weight: 0.45
        # TCI < 1.15 is LOW traffic (score 0.85-1.0)
        # 1.15 <= TCI < 1.40 is MEDIUM traffic (score 0.55-0.85)
        # TCI >= 1.40 is HIGH traffic (score 0.05-0.40 with heavy congestion penalty)
        tci = float(r.get("tci", fv.get("tci", 1.5)))
        if tci <= 1.15:
            tci_score = max(0.85, 1.0 - (tci - 1.0) * 0.5)
        elif tci < 1.40:
            tci_score = max(0.55, 0.85 - (tci - 1.15) * 1.2)
        else:
            tci_score = max(0.05, 0.40 - (tci - 1.40) * 0.4)

        # 2. Travel Time Efficiency Score — Weight: 0.35
        # Shorter duration is significantly better
        dur = float(r.get("duration_min", fv.get("duration_min", min_dur)))
        dur_score = 1.0 if dur_range < 0.1 else max(0.0, 1.0 - ((dur - min_dur) / dur_range))

        # 3. Distance Efficiency Score — Weight: 0.10
        dist = float(r.get("distance_km", fv.get("distance_km", min_dist)))
        dist_score = 1.0 if dist_range < 0.1 else max(0.0, 1.0 - ((dist - min_dist) / dist_range))

        # 4. Context & ML Score (CatBoost + Weather + Events) — Weight: 0.10
        raw_cb = float(r.get("raw_catboost_probability", 0.5))
        weather_risk = float(fv.get("weather_risk_score", 0.05))
        event_impact = float(fv.get("event_impact_score", 0.0))
        wp = float(fv.get("num_waypoints", 20))
        wp_score = max(0.0, 1.0 - (wp / 100.0))
        context_score = max(0.0, (
            raw_cb * 0.4 +
            (1.0 - weather_risk) * 0.25 +
            (1.0 - event_impact) * 0.25 +
            wp_score * 0.1
        ))

        # Balanced Composite Suitability
        composite_score = (
            0.45 * tci_score +
            0.35 * dur_score +
            0.10 * dist_score +
            0.10 * context_score
        )

        r["catboost_score"] = round(composite_score, 4)
        r["catboost_label"] = 1 if tci < 1.4 else 0

    # Ensure blocked routes have placeholder scores
    for i in blocked_indices:
        routes[i].setdefault("catboost_score", 0.0)
        routes[i].setdefault("catboost_label", 0)
        routes[i]["is_recommended"] = False

    # Step 4: Sort eligible routes by score descending (highest traffic/time suitability first)
    eligible_sorted = sorted(
        eligible_indices,
        key=lambda i: routes[i].get("catboost_score", 0.0),
        reverse=True,
    )

    # Step 5: Assign recommendation, rank, and clean road names
    import re
    recommended_assigned = False
    ranked_routes = []

    for rank, idx in enumerate(eligible_sorted, start=1):
        route = routes[idx]
        route["rank"] = rank

        # Clean existing prefixes so the best route is correctly named Fastest Route
        raw_name = route.get("name", "Corridor")
        clean_road = re.sub(
            r"^(?:Fastest Route\s*(?:via)?|Alternative\s*(?:via)?|Primary Route\s*(?:via)?|Route Option \d+\s*(?:via)?)\s*",
            "",
            raw_name,
            flags=re.IGNORECASE
        ).strip()
        if not clean_road:
            clean_road = f"Corridor {rank}"

        if not recommended_assigned:
            route["is_recommended"] = True
            route["name"] = f"Fastest Route via {clean_road}"
            recommended_assigned = True
        else:
            route["is_recommended"] = False
            route["name"] = f"Alternative via {clean_road}"

        ranked_routes.append(route)

    # Append blocked routes after all eligible ones
    for idx in blocked_indices:
        route = routes[idx]
        route["rank"] = len(eligible_sorted) + blocked_indices.index(idx) + 1
        raw_name = route.get("name", "Corridor")
        clean_road = re.sub(
            r"^(?:Fastest Route\s*(?:via)?|Alternative\s*(?:via)?|Primary Route\s*(?:via)?|Route Option \d+\s*(?:via)?)\s*",
            "",
            raw_name,
            flags=re.IGNORECASE
        ).strip() or f"Corridor {route['rank']}"
        route["name"] = f"Blocked via {clean_road}"
        ranked_routes.append(route)

    return ranked_routes
