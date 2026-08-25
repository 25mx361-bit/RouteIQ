from flask import Blueprint
from backend.controllers.notification_controller import (
    get_user_notifications_controller,
    mark_as_read_controller,
    mark_all_as_read_controller,
)

notification_routes_bp = Blueprint("notification_routes", __name__)

notification_routes_bp.route("/", methods=["GET"])(get_user_notifications_controller)
notification_routes_bp.route("/<notification_id>/read", methods=["PUT"])(mark_as_read_controller)
notification_routes_bp.route("/read-all", methods=["PUT"])(mark_all_as_read_controller)
