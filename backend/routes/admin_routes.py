from flask import Blueprint
from backend.middleware.auth_middleware import require_admin
from backend.controllers.admin_controller import (
    get_scheduler_info,
    trigger_scheduler_job,
    trigger_catboost_train,
    get_catboost_metrics,
    trigger_patchtst_train,
    get_patchtst_metrics,
    get_traffic_records,
    create_traffic_record,
    update_traffic_record,
    delete_traffic_record,
    get_all_predictions_list,
    get_reports_summary,
    check_api_status,
)
from backend.controllers.admin_users_controller import (
    list_users,
    update_user_role,
    deactivate_user,
    get_admin_stats,
    get_system_logs,
)

admin_routes_bp = Blueprint("admin_routes", __name__)

# ── Scheduler ────────────────────────────────────────────────────────────────
admin_routes_bp.get("/scheduler/status")(get_scheduler_info)
admin_routes_bp.post("/scheduler/trigger-job")(trigger_scheduler_job)

# ── CatBoost ML ──────────────────────────────────────────────────────────────
admin_routes_bp.post("/models/catboost/train")(require_admin(trigger_catboost_train))
admin_routes_bp.get("/models/catboost/metrics")(get_catboost_metrics)

# ── Users (admin only) ───────────────────────────────────────────────────────
admin_routes_bp.get("/users")(require_admin(list_users))
admin_routes_bp.put("/users/<user_id>/role")(require_admin(update_user_role))
admin_routes_bp.put("/users/<user_id>/deactivate")(require_admin(deactivate_user))

# ── Dashboard Stats (admin only) ─────────────────────────────────────────────
admin_routes_bp.get("/stats")(require_admin(get_admin_stats))

# ── System Logs (admin only) ─────────────────────────────────────────────────
admin_routes_bp.get("/logs")(require_admin(get_system_logs))



# -- PatchTST ML --------------------------------------------------------------
admin_routes_bp.post("/models/patchtst/train")(require_admin(trigger_patchtst_train))
admin_routes_bp.get("/models/patchtst/metrics")(get_patchtst_metrics)

# -- Phase 17 Admin Endpoints -------------------------------------------------
admin_routes_bp.get("/traffic")(require_admin(get_traffic_records))
admin_routes_bp.post("/traffic")(require_admin(create_traffic_record))
admin_routes_bp.put("/traffic/<record_id>")(require_admin(update_traffic_record))
admin_routes_bp.delete("/traffic/<record_id>")(require_admin(delete_traffic_record))
admin_routes_bp.get("/predictions-list")(require_admin(get_all_predictions_list))
admin_routes_bp.get("/reports/summary")(require_admin(get_reports_summary))
admin_routes_bp.get("/api-status")(require_admin(check_api_status))
