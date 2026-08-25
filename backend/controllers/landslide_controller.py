"""
backend/controllers/landslide_controller.py — Landslide Hazard & Route Blocking Controller.
"""
from __future__ import annotations

from flask import request, jsonify
from loguru import logger
from backend.services.landslide_service import LandslideService

landslide_service = LandslideService()


def list_landslides_controller():
    """Handle GET /api/landslides (Optional query ?status=ACTIVE)"""
    status = request.args.get("status", "").strip()
    try:
        hazards = landslide_service.list_landslides(status or None)
        return jsonify({
            "count": len(hazards),
            "landslides": hazards,
        }), 200
    except Exception as e:
        logger.error(f"Error listing landslides: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to fetch landslides."}), 500


def create_landslide_controller():
    """Handle POST /api/landslides (Admin only)"""
    body = request.get_json(silent=True) or {}
    try:
        hazard = landslide_service.create_landslide(body)
        return jsonify({
            "message": "Landslide hazard registered and broadcasted successfully.",
            "landslide": hazard,
        }), 201
    except ValueError as ve:
        return jsonify({"error": "validation_error", "message": str(ve)}), 422
    except Exception as e:
        logger.error(f"Error creating landslide: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to create landslide hazard."}), 500


def update_landslide_controller(landslide_id: str):
    """Handle PUT /api/landslides/<id> (Admin only)"""
    body = request.get_json(silent=True) or {}
    try:
        updated = landslide_service.update_landslide(landslide_id, body)
        if not updated:
            return jsonify({"error": "not_found", "message": f"Landslide '{landslide_id}' not found."}), 404
        return jsonify({
            "message": "Landslide updated successfully.",
            "landslide": updated,
        }), 200
    except Exception as e:
        logger.error(f"Error updating landslide {landslide_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to update landslide."}), 500


def delete_landslide_controller(landslide_id: str):
    """Handle DELETE /api/landslides/<id> (Admin only)"""
    try:
        success = landslide_service.delete_landslide(landslide_id)
        if not success:
            return jsonify({"error": "not_found", "message": f"Landslide '{landslide_id}' not found."}), 404
        return jsonify({
            "message": f"Landslide '{landslide_id}' deleted successfully.",
            "landslide_id": landslide_id,
        }), 200
    except Exception as e:
        logger.error(f"Error deleting landslide {landslide_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to delete landslide."}), 500


def activate_landslide_controller(landslide_id: str):
    """Handle PUT /api/landslides/<id>/activate (Admin only)"""
    try:
        hazard = landslide_service.activate_landslide(landslide_id)
        if not hazard:
            return jsonify({"error": "not_found", "message": f"Landslide '{landslide_id}' not found."}), 404
        return jsonify({
            "message": f"Landslide hazard activated. Road blockade enforced and notification broadcasted.",
            "landslide": hazard,
        }), 200
    except Exception as e:
        logger.error(f"Error activating landslide {landslide_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to activate landslide."}), 500


def resolve_landslide_controller(landslide_id: str):
    """Handle PUT /api/landslides/<id>/resolve (Admin only)"""
    try:
        hazard = landslide_service.resolve_landslide(landslide_id)
        if not hazard:
            return jsonify({"error": "not_found", "message": f"Landslide '{landslide_id}' not found."}), 404
        return jsonify({
            "message": f"Landslide hazard marked RESOLVED. Road restriction lifted.",
            "landslide": hazard,
        }), 200
    except Exception as e:
        logger.error(f"Error resolving landslide {landslide_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to resolve landslide."}), 500


def check_route_impact_controller():
    """Handle POST /api/landslides/check-route"""
    body = request.get_json(silent=True) or {}
    coordinates = body.get("coordinates", [])
    try:
        impact = landslide_service.check_route_landslide_impact(coordinates)
        return jsonify(impact), 200
    except Exception as e:
        logger.error(f"Error checking route landslide impact: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to evaluate landslide collision."}), 500
