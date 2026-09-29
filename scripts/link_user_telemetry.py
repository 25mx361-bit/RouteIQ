"""
scripts/link_user_telemetry.py
Link existing telemetry and default favorites to Sanjana user account
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import get_db
from datetime import datetime, timezone, timedelta
from bson import ObjectId

def run():
    db = get_db()
    sanjana = db.users.find_one({"email": "sanjana@customer.com"})
    if not sanjana:
        print("Sanjana not found")
        return
    sid = str(sanjana["_id"])
    print(f"Linking telemetry to Sanjana ({sid})...")
    
    # Assign some routes to Sanjana so she has recent personal routes and recommended routes
    routes = list(db.routes.find({"user_id": None}).limit(28))
    for r in routes:
        db.routes.update_one({"_id": r["_id"]}, {"$set": {"user_id": sid}})
    print(f"Updated {len(routes)} routes with user_id={sid}")

    # Also assign 12 CatBoost recommended routes to Sanjana
    rec_routes = list(db.routes.find({"is_recommended": True}).limit(12))
    for r in rec_routes:
        db.routes.update_one({"_id": r["_id"]}, {"$set": {"user_id": sid}})
    print(f"Updated {len(rec_routes)} recommended routes with user_id={sid}")
    
    # Assign some search history
    searches = list(db.search_history.find({"user_id": None}).limit(18))
    for s in searches:
        db.search_history.update_one({"_id": s["_id"]}, {"$set": {"user_id": sid}})
    print(f"Updated {len(searches)} search history with user_id={sid}")
    
    # Create 4 real favorite corridors if none exist
    if db.favorites.count_documents({"user_id": sid}) == 0:
        sample_favs = [
            {
                "user_id": sid,
                "source": {"label": "Gandhipuram Central", "lat": 11.0168, "lng": 76.9558},
                "destination": {"label": "Coimbatore Railway Junction", "lat": 10.9980, "lng": 76.9634},
                "route_name": "Gandhipuram ➔ Junction Expressway",
                "distance_km": 4.8,
                "duration_min": 12,
                "congestion_level": "LOW",
                "catboost_score": 0.94,
                "created_at": datetime.now(timezone.utc) - timedelta(days=2)
            },
            {
                "user_id": sid,
                "source": {"label": "PSG College of Technology", "lat": 11.0244, "lng": 77.0028},
                "destination": {"label": "Hopes College (Avinashi Rd)", "lat": 11.0275, "lng": 77.0150},
                "route_name": "Avinashi Road Direct Corridor",
                "distance_km": 2.3,
                "duration_min": 7,
                "congestion_level": "LOW",
                "catboost_score": 0.96,
                "created_at": datetime.now(timezone.utc) - timedelta(days=1)
            },
            {
                "user_id": sid,
                "source": {"label": "RS Puram (DB Road)", "lat": 11.0094, "lng": 76.9458},
                "destination": {"label": "Saibaba Colony", "lat": 11.0260, "lng": 76.9420},
                "route_name": "Mettupalayam Link Route",
                "distance_km": 3.6,
                "duration_min": 10,
                "congestion_level": "MEDIUM",
                "catboost_score": 0.88,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=14)
            },
            {
                "user_id": sid,
                "source": {"label": "Coimbatore Airport", "lat": 11.0298, "lng": 77.0434},
                "destination": {"label": "Peelamedu Tech Hub", "lat": 11.0244, "lng": 77.0028},
                "route_name": "Airport ➔ Tech Corridor Bypass",
                "distance_km": 5.2,
                "duration_min": 13,
                "congestion_level": "LOW",
                "catboost_score": 0.92,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=5)
            }
        ]
        db.favorites.insert_many(sample_favs)
        print("Created 4 sample favorites for Sanjana!")

    # Check counts
    print("Sanjana routes:", db.routes.count_documents({"user_id": sid}))
    print("Sanjana recommended:", db.routes.count_documents({"user_id": sid, "is_recommended": True}))
    print("Sanjana searches:", db.search_history.count_documents({"user_id": sid}))
    print("Sanjana favorites:", db.favorites.count_documents({"user_id": sid}))

if __name__ == "__main__":
    run()
