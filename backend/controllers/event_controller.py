"""
backend/controllers/event_controller.py — Public Events, Festivals & Marriages Controller.
"""
from __future__ import annotations

from datetime import datetime
from flask import request, jsonify, g
from loguru import logger
from backend.services.event_service import EventService

event_service = EventService()


def list_events_controller():
    """
    Handle GET /api/events
    Query params: type, status, date, lat, lng, radius_km
    """
    event_type = request.args.get("type", "").strip()
    status = request.args.get("status", "").strip()
    date_str = request.args.get("date", "").strip()
    lat_str = request.args.get("lat")
    lng_str = request.args.get("lng")
    radius_km = float(request.args.get("radius_km", 10.0))

    try:
        if lat_str and lng_str:
            lat = float(lat_str)
            lng = float(lng_str)
            events = event_service.get_active_events(lat, lng, radius_km)
        else:
            events = event_service.list_events(
                event_type=event_type or None,
                status=status or None,
                date_str=date_str or None,
            )

        return jsonify({
            "count": len(events),
            "events": events,
        }), 200
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return jsonify({
            "error": "internal_error",
            "message": "Failed to retrieve events.",
        }), 500


def create_event_controller():
    """
    Handle POST /api/events (Admin only)
    """
    body = request.get_json(silent=True) or {}
    try:
        event = event_service.create_event(body)
        return jsonify({
            "message": "Event created successfully.",
            "event": event,
        }), 201
    except ValueError as ve:
        return jsonify({"error": "validation_error", "message": str(ve)}), 422
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to create event."}), 500


def update_event_controller(event_id: str):
    """
    Handle PUT /api/events/<event_id> (Admin only)
    """
    body = request.get_json(silent=True) or {}
    try:
        updated = event_service.update_event(event_id, body)
        if not updated:
            return jsonify({"error": "not_found", "message": f"Event '{event_id}' not found."}), 404
        return jsonify({
            "message": "Event updated successfully.",
            "event": updated,
        }), 200
    except Exception as e:
        logger.error(f"Error updating event {event_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to update event."}), 500


def delete_event_controller(event_id: str):
    """
    Handle DELETE /api/events/<event_id> (Admin only)
    """
    try:
        success = event_service.delete_event(event_id)
        if not success:
            return jsonify({"error": "not_found", "message": f"Event '{event_id}' not found."}), 404
        return jsonify({
            "message": f"Event '{event_id}' deleted successfully.",
            "event_id": event_id,
        }), 200
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to delete event."}), 500


def evaluate_route_impact_controller():
    """
    Handle POST /api/events/route-impact
    Body: { "coordinates": [[lat, lng], ...], "datetime": "YYYY-MM-DDTHH:MM:SS" }
    """
    body = request.get_json(silent=True) or {}
    coordinates = body.get("coordinates", [])
    datetime_str = body.get("datetime")

    target_dt = None
    if datetime_str:
        try:
            target_dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except Exception:
            pass

    try:
        impact = event_service.evaluate_route_events(coordinates, target_dt)
        return jsonify(impact), 200
    except Exception as e:
        logger.error(f"Error evaluating route events impact: {e}")
        return jsonify({"error": "internal_error", "message": "Failed to evaluate route impact."}), 500
