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

    # Step 2: Score eligible routes with CatBoost
    if use_catboost and eligible_indices:
        try:
            from ml.catboost.prediction import predict_route_scores
            eligible_fvs = [feature_vectors[i] for i in eligible_indices]
            scores = predict_route_scores(eligible_fvs)
            for score_result in scores:
                route_idx = eligible_indices[score_result["route_index"]]
                routes[route_idx]["catboost_score"] = score_result["score"]
                routes[route_idx]["catboost_label"] = score_result["label"]
        except FileNotFoundError:
            logger.warning(
                "CatBoost model not found. Falling back to TCI-based ranking."
            )
            use_catboost = False
        except Exception as exc:
            logger.error(f"CatBoost scoring failed: {exc}. Falling back to TCI ranking.")
            use_catboost = False

    # Fallback ranking: multi-factor scoring (lower is better for each penalty)
    if not use_catboost:
        for i in eligible_indices:
            fv = feature_vectors[i]
            r = routes[i]

            # Lower TCI = less congestion = better (weight: 0.35)
            tci = fv.get("tci", 1.5)
            tci_score = max(0.0, 1.0 - (tci - 1.0) / 2.5)

            # Shorter distance = better (weight: 0.30) — normalize to 0-1
            all_dists = [feature_vectors[j].get("distance_km", 10) for j in eligible_indices]
            max_d = max(all_dists) if all_dists else 10
            min_d = min(all_dists) if all_dists else 1
            dist = fv.get("distance_km", max_d)
            dist_score = 1.0 - ((dist - min_d) / (max_d - min_d + 0.001))

            # Fewer waypoints = simpler path = better (weight: 0.15)
            wp = fv.get("num_waypoints", 20)
            wp_score = max(0.0, 1.0 - (wp / 100.0))

            # Lower weather risk = better (weight: 0.10)
            weather_score = max(0.0, 1.0 - fv.get("weather_risk_score", 0.05))

            # Fewer event impacts = better (weight: 0.10)
            event_score = max(0.0, 1.0 - fv.get("event_impact_score", 0.0))

            combined_score = (
                0.35 * tci_score +
                0.30 * dist_score +
                0.15 * wp_score +
                0.10 * weather_score +
                0.10 * event_score
            )

            routes[i]["catboost_score"] = round(combined_score, 4)
            routes[i]["catboost_label"] = 1 if tci < 1.4 else 0


    # Ensure blocked routes have placeholder scores
    for i in blocked_indices:
        routes[i].setdefault("catboost_score", 0.0)
        routes[i].setdefault("catboost_label", 0)
        routes[i]["is_recommended"] = False

    # Step 3: Sort eligible routes by score descending
    eligible_sorted = sorted(
        eligible_indices,
        key=lambda i: routes[i].get("catboost_score", 0.0),
        reverse=True,
    )

    # Step 4: Assign recommendation and rank
    recommended_assigned = False
    ranked_routes = []

    for rank, idx in enumerate(eligible_sorted, start=1):
        route = routes[idx]
        route["rank"] = rank
        if not recommended_assigned:
            route["is_recommended"] = True
            recommended_assigned = True
        else:
            route["is_recommended"] = False
        ranked_routes.append(route)

    # Append blocked routes after all eligible ones
    for idx in blocked_indices:
        route = routes[idx]
        route["rank"] = len(eligible_sorted) + blocked_indices.index(idx) + 1
        ranked_routes.append(route)

    return ranked_routes
