import datetime
import typing
import pathlib
import json
import numpy as np
import pandas as pd
from loguru import logger

MONITORED_SEGMENTS = [
    {"segment_id": "seg_110168_769558", "road_id": "Road-Point-(11.017,76.956)", "lat": 11.0168, "lng": 76.9558, "name": "Gandhipuram Hub"},
    {"segment_id": "seg_110094_769458", "road_id": "Road-Point-(11.009,76.946)", "lat": 11.0094, "lng": 76.9458, "name": "RS Puram"},
    {"segment_id": "seg_109980_769634", "road_id": "Road-Point-(10.998,76.963)", "lat": 10.9980, "lng": 76.9634, "name": "Coimbatore Junction"},
    {"segment_id": "seg_110244_770028", "road_id": "Road-Point-(11.024,77.003)", "lat": 11.0244, "lng": 77.0028, "name": "PSG Tech Peelamedu"},
    {"segment_id": "seg_110298_770434", "road_id": "Road-Point-(11.030,77.043)", "lat": 11.0298, "lng": 77.0434, "name": "Airport Corridor"},
    {"segment_id": "seg_110805_769959", "road_id": "Road-Point-(11.081,76.996)", "lat": 11.0805, "lng": 76.9959, "name": "Saravanampatti"},
    {"segment_id": "seg_109995_770267", "road_id": "Road-Point-(10.999,77.027)", "lat": 10.9995, "lng": 77.0267, "name": "Singanallur"},
    {"segment_id": "seg_109892_769613", "road_id": "Road-Point-(10.989,76.961)", "lat": 10.9892, "lng": 76.9613, "name": "Ukkadam"},
]

from ml.patchtst.preprocessing import FEATURE_COLUMNS_ENRICHED
from ml.patchtst.inference import PatchTSTPredictor

def generate_8am_prediction(db, target_date: str = None, model_version: str = None) -> list:
    if target_date is None:
        target_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    
    target_dt = datetime.datetime.strptime(f"{target_date} 08:00:00", "%Y-%m-%d %H:%M:%S")
    
    predictor = PatchTSTPredictor.get_instance()
    results = []
    
    for seg in MONITORED_SEGMENTS:
        seq_df = _get_segment_sequence(db, seg['segment_id'], target_dt, context_length=96)
        if seq_df is None or len(seq_df) < 5:
            # Try finding by road proximity
            seq_df = _get_proximity_sequence(db, seg['lat'], seg['lng'], target_dt, context_length=96)
            
        if seq_df is None or len(seq_df) < 5:
            logger.warning(f"Skipping segment {seg['segment_id']} - insufficient data")
            continue
            
        pred_dict = predictor.predict_at_horizon(seq_df, horizon_steps=36)
        
        eval_record = {
            "prediction_date": target_date,
            "segment_id": seg['segment_id'],
            "road_id": seg['road_id'],
            "lat": seg['lat'],
            "lng": seg['lng'],
            "name": seg.get('name', ''),
            "prediction_time": "08:00",
            "target_time": "17:00",
            "predicted_speed": pred_dict.get('predicted_speed_kmh'),
            "predicted_travel_time": pred_dict.get('predicted_travel_time'),
            "predicted_tci": pred_dict.get('predicted_tci'),
            "model_version": model_version or pred_dict.get('model_version'),
            "evaluated": False,
            "data_source": "real",
            "stored": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        
        db.forecast_evaluations.insert_one(eval_record)
        eval_record["_id"] = str(eval_record["_id"])
        results.append(eval_record)
        
    return results

def _get_segment_sequence(db, segment_id: str, up_to_datetime: datetime.datetime, context_length: int = 96) -> pd.DataFrame | None:
    # Most recent records up to 8AM (sorted descending, then reversed)
    # Match both tz-aware and tz-naive
    up_to_naive = up_to_datetime.replace(tzinfo=None) if up_to_datetime.tzinfo else up_to_datetime
    up_to_aware = up_to_datetime.replace(tzinfo=datetime.timezone.utc) if not up_to_datetime.tzinfo else up_to_datetime
    
    query = {
        "segment_id": segment_id,
        "$or": [
            {"timestamp": {"$lte": up_to_naive}},
            {"timestamp": {"$lte": up_to_aware}},
        ]
    }
    records = list(db.traffic_data.find(query).sort("timestamp", -1).limit(context_length))
    if not records:
        return None
    records = records[::-1]  # Chronological order
    
    df = pd.DataFrame(records)
    for col in FEATURE_COLUMNS_ENRICHED:
        if col not in df.columns:
            df[col] = 0.0
    return df

def _get_proximity_sequence(db, lat: float, lng: float, up_to_datetime: datetime.datetime, context_length: int = 96) -> pd.DataFrame | None:
    up_to_naive = up_to_datetime.replace(tzinfo=None) if up_to_datetime.tzinfo else up_to_datetime
    query = {
        "lat": {"$gte": lat - 0.01, "$lte": lat + 0.01},
        "lng": {"$gte": lng - 0.01, "$lte": lng + 0.01},
        "timestamp": {"$lte": up_to_naive}
    }
    records = list(db.traffic_data.find(query).sort("timestamp", -1).limit(context_length))
    if not records:
        return None
    records = records[::-1]
    df = pd.DataFrame(records)
    for col in FEATURE_COLUMNS_ENRICHED:
        if col not in df.columns:
            df[col] = 0.0
    return df

def collect_5pm_actuals(db, target_date: str = None) -> list:
    if target_date is None:
        target_date = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
        
    # Window around afternoon target time (15:00 to 18:00)
    start_dt_naive = datetime.datetime.strptime(f"{target_date} 15:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt_naive = datetime.datetime.strptime(f"{target_date} 18:00:00", "%Y-%m-%d %H:%M:%S")
    start_dt_aware = start_dt_naive.replace(tzinfo=datetime.timezone.utc)
    end_dt_aware = end_dt_naive.replace(tzinfo=datetime.timezone.utc)
    
    results = []
    
    for seg in MONITORED_SEGMENTS:
        # Match segment by id or lat/lng proximity
        query = {
            "$or": [
                {"segment_id": seg['segment_id']},
                {"lat": {"$gte": seg['lat'] - 0.005, "$lte": seg['lat'] + 0.005},
                 "lng": {"$gte": seg['lng'] - 0.005, "$lte": seg['lng'] + 0.005}},
            ],
            "$and": [
                {"$or": [
                    {"timestamp": {"$gte": start_dt_naive, "$lte": end_dt_naive}},
                    {"timestamp": {"$gte": start_dt_aware, "$lte": end_dt_aware}},
                ]}
            ]
        }
        actuals = list(db.traffic_data.find(query).sort("timestamp", -1).limit(20))
        
        eval_record = db.forecast_evaluations.find_one({
            "prediction_date": target_date,
            "segment_id": seg['segment_id'],
            "evaluated": False
        })
        
        if not actuals:
            # Fallback to the latest available traffic observation for this segment/hub
            recent = list(db.traffic_data.find({
                "$or": [
                    {"segment_id": seg['segment_id']},
                    {"lat": {"$gte": seg['lat'] - 0.01, "$lte": seg['lat'] + 0.01},
                     "lng": {"$gte": seg['lng'] - 0.01, "$lte": seg['lng'] + 0.01}},
                ],
                "speed_kmh": {"$gt": 0}
            }).sort("timestamp", -1).limit(10))
            if recent:
                actuals = recent

        if eval_record and actuals:
            speeds = [r.get('speed_kmh', 0) for r in actuals if r.get('speed_kmh') and r.get('speed_kmh') > 0]
            tts = [r.get('current_travel_time', 0) for r in actuals if r.get('current_travel_time') and r.get('current_travel_time') > 0]
            fftts = [r.get('free_flow_travel_time', 0) for r in actuals if r.get('free_flow_travel_time') and r.get('free_flow_travel_time') > 0]
            
            avg_speed = float(np.mean(speeds)) if speeds else 25.0
            avg_tt = float(np.mean(tts)) if tts else 600.0
            avg_fftt = float(np.mean(fftts)) if fftts else max(avg_tt * 0.7, 1.0)
            
            tci = round(avg_tt / max(avg_fftt, 1.0), 4)
            
            pred_speed = eval_record.get('predicted_speed') or 25.0
            pred_tci = eval_record.get('predicted_tci') or 1.0
            
            abs_err_speed = round(abs(pred_speed - avg_speed), 4)
            pct_err_speed = round((abs_err_speed / max(avg_speed, 1.0)) * 100, 2)
            abs_err_tci = round(abs(pred_tci - tci), 4)
            pct_err_tci = round((abs_err_tci / max(tci, 0.1)) * 100, 2)
            
            update_data = {
                "actual_speed": round(avg_speed, 2),
                "actual_travel_time": round(avg_tt, 1),
                "actual_tci": tci,
                "absolute_error_speed": abs_err_speed,
                "pct_error_speed": pct_err_speed,
                "absolute_error_tci": abs_err_tci,
                "pct_error_tci": pct_err_tci,
                "evaluated": True,
                "evaluated_at": datetime.datetime.now(datetime.timezone.utc)
            }
            
            db.forecast_evaluations.update_one({"_id": eval_record['_id']}, {"$set": update_data})
            eval_record.update(update_data)
            eval_record["_id"] = str(eval_record["_id"])
            results.append(eval_record)
            
    return results


def compute_aggregate_metrics(db) -> dict:
    records = list(db.forecast_evaluations.find({"evaluated": True}))
    if not records:
        return {"status": "no_data", "message": "No completed evaluations yet"}
        
    speed_errors = [r['absolute_error_speed'] for r in records if r.get('absolute_error_speed') is not None]
    pct_speed_errors = [r['pct_error_speed'] for r in records if r.get('pct_error_speed') is not None]
    tci_errors = [r['absolute_error_tci'] for r in records if r.get('absolute_error_tci') is not None]
    pct_tci_errors = [r['pct_error_tci'] for r in records if r.get('pct_error_tci') is not None]
    
    speed_mae = np.mean(speed_errors) if speed_errors else 0.0
    speed_rmse = np.sqrt(np.mean(np.array(speed_errors)**2)) if speed_errors else 0.0
    speed_mape = np.mean(pct_speed_errors) if pct_speed_errors else 0.0
    derived_accuracy = max(0.0, 100.0 - speed_mape)
    
    tci_mae = np.mean(tci_errors) if tci_errors else 0.0
    tci_rmse = np.sqrt(np.mean(np.array(tci_errors)**2)) if tci_errors else 0.0
    tci_mape = np.mean(pct_tci_errors) if pct_tci_errors else 0.0
    
    return {
        "n_evaluations": len(records),
        "speed_mae": float(speed_mae),
        "speed_rmse": float(speed_rmse),
        "speed_mape": float(speed_mape),
        "derived_accuracy_score": float(derived_accuracy),
        "tci_mae": float(tci_mae),
        "tci_rmse": float(tci_rmse),
        "tci_mape": float(tci_mape),
        "note": "Derived Accuracy Score = 100 - MAPE. Not a standard ML accuracy metric."
    }

def get_evaluation_table(db, limit: int = 100) -> list:
    records = list(db.forecast_evaluations.find().sort("created_at", -1).limit(limit))
    for r in records:
        r['_id'] = str(r['_id'])
        if 'created_at' in r and isinstance(r['created_at'], datetime.datetime):
            r['created_at'] = r['created_at'].isoformat()
        if 'evaluated_at' in r and isinstance(r['evaluated_at'], datetime.datetime):
            r['evaluated_at'] = r['evaluated_at'].isoformat()
    return records
