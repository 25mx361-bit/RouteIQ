"""
scripts/seed_traffic_data.py — Seed MongoDB traffic_data collection with realistic temporal telemetry.
Populates historical 90-day time-series including today's full timeline for validation.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database import get_db
from ml.patchtst.dataset import generate_realistic_traffic_timeseries

def seed_traffic_data(days=90):
    db = get_db()
    collection = db["traffic_data"]
    
    print(f"[*] Generating {days} days of realistic traffic records with rush-hour & weather dynamics...")
    start_dt = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    df = generate_realistic_traffic_timeseries(start_date=start_dt, days=days)
    
    # Format documents for MongoDB
    records = []
    for _, row in df.iterrows():
        ts = row["timestamp"].to_pydatetime()
        records.append({
            "segment_id": "seg_coimbatore_corridor",
            "road_id": "Avinashi-Trichy-Corridor",
            "timestamp": ts,
            "speed_kmh": float(row["speed_kmh"]),
            "current_travel_time": float(row["current_travel_time"]),
            "free_flow_speed": float(row["free_flow_speed"]),
            "free_flow_travel_time": float(row["free_flow_travel_time"]),
            "temperature": float(row["temperature"]),
            "precipitation": float(row["precipitation"]),
            "confidence": 0.95,
            "source": "routeiq_telemetry_engine",
        })
        
    print(f"[*] Inserting {len(records)} records into MongoDB traffic_data collection...")
    # Clean previous synthetic records to maintain high quality
    collection.delete_many({"source": "routeiq_telemetry_engine"})
    collection.insert_many(records)
    print(f"[+] Successfully seeded {len(records)} traffic records into MongoDB!")

if __name__ == "__main__":
    days_to_seed = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    seed_traffic_data(days_to_seed)
