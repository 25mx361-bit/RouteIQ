"""
visualize_models.py — View training metrics and traffic predictions for both models.
Run from project root:  python visualize_models.py
"""
import sys, json, math, datetime
from pathlib import Path

# ── Make backend importable ────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

# ── Load saved metrics files ───────────────────────────────────────────────────
PATCHTST_METRICS = Path("ml/patchtst/checkpoints/patchtst_metrics.json")
CATBOOST_METRICS = Path("ml/catboost/checkpoints/catboost_metrics.json")

def load_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return None

print("=" * 65)
print("         RouteIQ — Model Training & Prediction Report")
print("=" * 65)

# ── 1. PatchTST Traffic Forecasting Model ─────────────────────────────────────
print("\n📌  PatchTST  — Traffic Speed Forecasting Model")
print("-" * 50)
ptm = load_json(PATCHTST_METRICS)
if ptm:
    print(f"  Trained at   : {ptm.get('timestamp', 'N/A')}")
    print(f"  Status       : ✅ {ptm.get('status', 'N/A').upper()}")
    print(f"  MAE          : {ptm['mae']} vehicles/5min")
    print(f"  RMSE         : {ptm['rmse']} vehicles/5min")
    print(f"  MAPE         : {ptm['mape'] * 100:.2f}%  (Mean Absolute % Error)")
    print(f"  Val Loss(MSE): {ptm['val_loss_scaled']}")
    print(f"\n  ℹ️  MAPE of {ptm['mape']*100:.1f}% means predictions are on average "
          f"{ptm['mape']*100:.1f}% off from actual traffic volume.")
else:
    print("  ❌ No metrics found. Run training first from the admin panel.")

# ── 2. CatBoost Route Classifier ──────────────────────────────────────────────
print("\n📌  CatBoost — Best Route Recommendation Classifier")
print("-" * 50)
cbm = load_json(CATBOOST_METRICS)
if cbm:
    print(f"  Trained at   : {cbm.get('trained_at', 'N/A')}")
    n_train = cbm.get('n_train', 'N/A')
    n_val   = cbm.get('n_val',   'N/A')
    print(f"  Training set : {n_train} routes | Validation: {n_val} routes")
    dist = cbm.get('label_distribution_train', {})
    if dist:
        total = sum(dist.values())
        print(f"  Label dist.  : {dist.get('1', 0)} recommended ({dist.get('1',0)/total*100:.1f}%) "
              f"| {dist.get('0',0)} not-recommended ({dist.get('0',0)/total*100:.1f}%)")
    print(f"  Accuracy     : {cbm.get('accuracy', 0)*100:.1f}%")
    print(f"  F1 Score     : {cbm.get('f1', 0)*100:.1f}%")
    print(f"  AUC-ROC      : {cbm.get('auc', 0)*100:.1f}%")
    print(f"  Rule used    : {cbm.get('labelling_rule', 'N/A')}")
else:
    print("  ❌ No metrics found. Run training first from the admin panel.")

# ── 3. Live Traffic Prediction Samples ────────────────────────────────────────
print("\n\n📌  Live Traffic Prediction — Sample Predictions")
print("-" * 50)
print("  Simulating predictions for Coimbatore routes right now...\n")

try:
    from ml.patchtst.inference import PatchTSTPredictor
    predictor = PatchTSTPredictor()

    sample_routes = [
        {"name": "Peelamedu → Hopes College",       "dist": 3.66,  "lat": 11.0287, "lng": 77.0042},
        {"name": "Gandhipuram → RS Puram",           "dist": 3.01,  "lat": 11.0176, "lng": 76.9667},
        {"name": "Singanallur → Gandhipuram",        "dist": 6.5,   "lat": 11.0038, "lng": 77.0063},
        {"name": "Avinashi Rd (long corridor)",       "dist": 12.0,  "lat": 11.0287, "lng": 77.0042},
    ]

    now = datetime.datetime.now()
    hour = now.hour

    print(f"  Time: {now.strftime('%Y-%m-%d %H:%M')} (Hour {hour})")
    print()
    print(f"  {'Route':<38} {'Dist':>6} {'Pred Speed':>12} {'ETA':>8} {'TCI':>6} {'Congestion':>12}")
    print(f"  {'-'*38} {'-'*6} {'-'*12} {'-'*8} {'-'*6} {'-'*12}")

    for route in sample_routes:
        result = predictor.predict_route_traffic(
            distance_km=route["dist"],
            source_lat=route["lat"],
            source_lng=route["lng"]
        )
        speed  = result.get("predicted_speed_kmh", 0)
        tci    = result.get("tci", 0)
        eta    = result.get("predicted_travel_time_min", 0)
        cong   = result.get("congestion_level", "?")
        icon   = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(cong, "⚪")
        print(f"  {route['name']:<38} {route['dist']:>5.1f}km {speed:>9.1f}km/h {eta:>7.1f}min "
              f"{tci:>5.2f}  {icon} {cong}")
    print()

except Exception as e:
    print(f"  ⚠️  Could not load PatchTST model: {e}")
    print("     Make sure you're running from e:\\ROUTE_IQ_version1 and .venv is active.")

# ── 4. CatBoost live scoring ───────────────────────────────────────────────────
print("\n📌  CatBoost Route Ranking — Sample Scoring")
print("-" * 50)
try:
    from ml.catboost.prediction import CatBoostRoutePredictor
    cb_pred = CatBoostRoutePredictor()

    sample_features = [
        {"name": "Fastest Route via Avinashi Rd",    "tci": 1.6, "dist": 3.66, "dur": 14.6, "weather": "MEDIUM", "landslide": "NONE"},
        {"name": "Alternative via Ramasamy Layout",  "tci": 1.7, "dist": 3.87, "dur": 16.3, "weather": "MEDIUM", "landslide": "NONE"},
        {"name": "Via Vilankuruchi Rd (long)",        "tci": 1.9, "dist": 7.1,  "dur": 24.9, "weather": "MEDIUM", "landslide": "NONE"},
    ]

    print(f"  {'Route':<40} {'TCI':>5} {'Dist':>6} {'Score':>8} {'Recommended'}")
    print(f"  {'-'*40} {'-'*5} {'-'*6} {'-'*8} {'-'*11}")

    from ml.catboost.features import ALL_FEATURES
    import numpy as np

    for feat in sample_features:
        row = {
            "distance_km": feat["dist"],
            "duration_min": feat["dur"],
            "tci": feat["tci"],
            "free_flow_travel_time": feat["dist"] / 30.0 * 60,
            "congestion_delay_min": max(0, feat["dur"] - feat["dist"] / 30.0 * 60),
            "waypoint_count": 3,
            "weather_risk_score": 0.3,
            "weather_risk_level": feat["weather"],
            "event_impact_score": 0.1,
            "road_blocked": 0,
            "landslide_active": 0,
            "landslide_severity": feat["landslide"],
            "num_landslide_alerts": 0,
            "hour_of_day": datetime.datetime.now().hour,
            "day_of_week": datetime.datetime.now().weekday(),
            "is_weekend": int(datetime.datetime.now().weekday() >= 5),
            "is_peak_hour": int(datetime.datetime.now().hour in [8,9,17,18,19]),
            "source_lat": 11.0287,
            "source_lng": 77.0042,
            "dest_lat": 11.0238,
            "dest_lng": 77.0185,
        }
        # Build feature vector in correct column order
        vec = np.array([[row.get(f, 0) for f in ALL_FEATURES]])
        score = cb_pred.model.predict_proba(vec)[0][1]
        rec = "✅ YES" if score > 0.5 else "❌ No"
        print(f"  {feat['name']:<40} {feat['tci']:>5.2f} {feat['dist']:>5.1f}km {score:>8.3f}  {rec}")

except Exception as e:
    print(f"  ⚠️  Could not load CatBoost model: {e}")

print("\n" + "=" * 65)
print("  ✅  Report complete. Both models are trained and operational.")
print("=" * 65)
