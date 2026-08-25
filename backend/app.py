"""
app.py — Flask Application Factory for RouteIQ
================================================
Follows the application factory pattern so the app instance can be created
with different configurations (development, testing, production).

Usage:
    flask --app backend.app run --debug         # development
    python backend/app.py                        # direct run
"""
import sys
from pathlib import Path

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from loguru import logger

from backend.config.settings import get_config, BaseConfig
from backend.extensions import mongo, scheduler
from backend.database import init_db


def create_app(config: BaseConfig | None = None) -> Flask:
    """
    Flask application factory.

    Args:
        config: Optional config object. If None, auto-selects via APP_ENV env var.

    Returns:
        Configured Flask application instance.
    """
    cfg = config or get_config()

    # -------------------------------------------------------------------------
    # Core Flask app
    # -------------------------------------------------------------------------
    app = Flask(__name__, instance_relative_config=False)

    # Load configuration onto the app
    app.config["SECRET_KEY"] = cfg.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = cfg.JWT_SECRET_KEY
    app.config["MONGO_URI"] = cfg.MONGO_URI
    app.config["SCHEDULER_API_ENABLED"] = cfg.SCHEDULER_API_ENABLED
    app.config["DEBUG"] = cfg.DEBUG
    app.config["ROUTEIQ_CONFIG"] = cfg

    # -------------------------------------------------------------------------
    # Configure structured logging (loguru)
    # -------------------------------------------------------------------------
    _configure_logging(cfg)

    # -------------------------------------------------------------------------
    # CORS — allow React dev server and production origins
    # -------------------------------------------------------------------------
    CORS(
        app,
        resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # -------------------------------------------------------------------------
    # Extensions & Pure PyMongo Database Initialisation
    # -------------------------------------------------------------------------
    JWTManager(app)
    try:
        mongo.init_app(app)
    except Exception as e:
        logger.warning(f"flask_pymongo init notice: {e}")

    try:
        init_db(cfg.MONGO_URI)
    except Exception as e:
        logger.warning(f"MongoDB connection notice during app start: {e}")

    # -------------------------------------------------------------------------
    # Blueprints — register all API routes under /api/v1/
    # -------------------------------------------------------------------------
    _register_blueprints(app)

    # -------------------------------------------------------------------------
    # Global error handlers
    # -------------------------------------------------------------------------
    _register_error_handlers(app)

    # -------------------------------------------------------------------------
    # Health-check root endpoint
    # -------------------------------------------------------------------------
    @app.get("/")
    def root():
        return jsonify({"status": "ok", "service": cfg.APP_NAME, "version": cfg.API_VERSION})

    # Start APScheduler background engine
    try:
        from backend.scheduler.scheduler import init_scheduler, start_scheduler
        init_scheduler(app)
        start_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler startup notice: {e}")

    logger.info(f"RouteIQ API started — env={app.config.get('ENV','development')} debug={cfg.DEBUG}")
    return app


# -----------------------------------------------------------------------------
# Private helpers
# -----------------------------------------------------------------------------

def _configure_logging(cfg: BaseConfig) -> None:
    """Configure loguru sink for console and file output."""
    import sys
    from loguru import logger

    logger.remove()

    logger.add(
        sys.stdout,
        level=cfg.LOG_LEVEL,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    )

    log_dir = cfg.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        log_dir / "routeiq_{time:YYYY-MM-DD}.log",
        level=cfg.LOG_LEVEL,
        rotation="00:00",
        retention="14 days",
        compression="zip",
        enqueue=True,
    )


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    from backend.routes.auth_routes import auth_routes_bp
    from backend.routes.geocoding_routes import geocoding_routes_bp
    from backend.routes.route_routes import route_routes_bp
    from backend.routes.traffic_routes import traffic_routes_bp
    from backend.routes.weather_routes import weather_routes_bp
    from backend.routes.admin_routes import admin_routes_bp
    from backend.routes.event_routes import event_routes_bp
    from backend.routes.landslide_routes import landslide_routes_bp
    from backend.api.v1.routes.prediction import prediction_bp

    # Auth routes at /api/auth and /api/v1/auth
    app.register_blueprint(auth_routes_bp, url_prefix="/api/auth")
    app.register_blueprint(auth_routes_bp, url_prefix="/api/v1/auth", name_prefix="v1_")

    # Geocoding routes at /api/geocode and /api/v1/geocode
    app.register_blueprint(geocoding_routes_bp, url_prefix="/api")
    app.register_blueprint(geocoding_routes_bp, url_prefix="/api/v1", name_prefix="v1_geo_")

    # Routing & Alternatives at /api/routes and /api/v1/routing
    app.register_blueprint(route_routes_bp, url_prefix="/api/routes")
    app.register_blueprint(route_routes_bp, url_prefix="/api/v1/routing", name_prefix="v1_routing_")

    # Traffic flow endpoints at /api/traffic and /api/v1/traffic
    app.register_blueprint(traffic_routes_bp, url_prefix="/api/traffic")
    app.register_blueprint(traffic_routes_bp, url_prefix="/api/v1/traffic", name_prefix="v1_traffic_")

    # Weather endpoints at /api/weather and /api/v1/weather
    app.register_blueprint(weather_routes_bp, url_prefix="/api/weather")
    app.register_blueprint(weather_routes_bp, url_prefix="/api/v1/weather", name_prefix="v1_weather_")

    # Admin & Scheduler endpoints at /api/admin and /api/v1/admin
    app.register_blueprint(admin_routes_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_routes_bp, url_prefix="/api/v1/admin", name_prefix="v1_admin_")

    # Events, Festivals & Marriages at /api/events and /api/v1/events
    app.register_blueprint(event_routes_bp, url_prefix="/api/events")
    app.register_blueprint(event_routes_bp, url_prefix="/api/v1/events", name_prefix="v1_events_")

    # Landslide hazards & blockages at /api/landslides and /api/v1/landslides
    app.register_blueprint(landslide_routes_bp, url_prefix="/api/landslides")
    app.register_blueprint(landslide_routes_bp, url_prefix="/api/v1/landslides", name_prefix="v1_landslides_")

    # Notifications at /api/notifications and /api/v1/notifications
    from backend.routes.notification_routes import notification_routes_bp
    app.register_blueprint(notification_routes_bp, url_prefix="/api/notifications")
    app.register_blueprint(notification_routes_bp, url_prefix="/api/v1/notifications", name_prefix="v1_notifications_")

    API_PREFIX = "/api/v1"
    app.register_blueprint(prediction_bp,  url_prefix=f"{API_PREFIX}/prediction")

    logger.debug("Blueprints registered: auth_routes, geocoding_routes, route_routes, traffic_routes, weather_routes, admin_routes, event_routes, landslide_routes, prediction, notification_routes")


def _register_error_handlers(app: Flask) -> None:
    """Register global JSON error handlers."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad_request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "unauthorized", "message": str(e)}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found", "message": str(e)}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "unprocessable_entity", "message": str(e)}), 422

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled exception")
        return jsonify({"error": "internal_server_error", "message": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
