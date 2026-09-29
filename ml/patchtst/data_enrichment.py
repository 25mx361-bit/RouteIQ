"""
ml/patchtst/data_enrichment.py — Traffic + Weather Data Enrichment.

Joins traffic_data with weather_data by nearest timestamp.
Handles column name conflicts, timezone normalization, and data source labeling.
"""
import pandas as pd
import numpy as np
from loguru import logger


def _normalize_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure timestamp column is UTC-naive datetime for merge_asof compatibility."""
    if 'timestamp' in df.columns:
        df = df.copy()
        ts = pd.to_datetime(df['timestamp'], utc=False)
        if hasattr(ts, 'dt') and ts.dt.tz is not None:
            ts = ts.dt.tz_localize(None)
        df['timestamp'] = ts
    return df


def enrich_traffic_with_weather(traffic_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich traffic records with weather data via nearest-timestamp merge.
    Renames weather columns before merge to avoid collision with existing traffic columns.
    """
    if traffic_df.empty:
        return traffic_df

    traffic_df = _normalize_timestamp(traffic_df.copy())

    if weather_df.empty:
        for col, default in [('temperature', 28.0), ('precipitation', 0.0), ('humidity', 65.0), ('wind_speed', 10.0)]:
            if col not in traffic_df.columns:
                traffic_df[col] = default
            else:
                traffic_df[col] = traffic_df[col].fillna(default)
        return traffic_df

    weather_df = _normalize_timestamp(weather_df.copy()).sort_values('timestamp')
    traffic_df = traffic_df.sort_values('timestamp')

    # Rename weather columns to avoid pandas suffix collision
    w_rename = {}
    w_select = ['timestamp']
    if 'temperature' in weather_df.columns:
        w_rename['temperature'] = '_w_temp'
        w_select.append('temperature')
    if 'rainfall_mm' in weather_df.columns:
        w_select.append('rainfall_mm')
    if 'humidity_pct' in weather_df.columns:
        w_select.append('humidity_pct')
    if 'wind_speed' in weather_df.columns:
        w_rename['wind_speed'] = '_w_wind'
        w_select.append('wind_speed')

    weather_sub = weather_df[w_select].rename(columns=w_rename).drop_duplicates(subset=['timestamp'])

    try:
        merged = pd.merge_asof(
            traffic_df,
            weather_sub,
            on='timestamp',
            tolerance=pd.Timedelta(hours=1),
            direction='nearest',
        )
    except Exception as e:
        logger.warning(f"merge_asof failed ({e}). Using default weather values.")
        merged = traffic_df.copy()

    # Map renamed columns back, filling from existing traffic col if NaN
    if '_w_temp' in merged.columns:
        existing = merged['temperature'] if 'temperature' in merged.columns else None
        merged['temperature'] = merged['_w_temp'].fillna(existing if existing is not None else 28.0)
        merged.drop(columns=['_w_temp'], inplace=True, errors='ignore')
    elif 'temperature' not in merged.columns:
        merged['temperature'] = 28.0
    else:
        merged['temperature'] = merged['temperature'].fillna(28.0)

    if 'rainfall_mm' in merged.columns:
        merged['precipitation'] = merged['rainfall_mm'].fillna(
            merged['precipitation'] if 'precipitation' in merged.columns else 0.0
        )
    elif 'precipitation' not in merged.columns:
        merged['precipitation'] = 0.0
    else:
        merged['precipitation'] = merged['precipitation'].fillna(0.0)

    if 'humidity_pct' in merged.columns:
        merged['humidity'] = merged['humidity_pct'].fillna(65.0)
    elif 'humidity' not in merged.columns:
        merged['humidity'] = 65.0
    else:
        merged['humidity'] = merged['humidity'].fillna(65.0)

    if '_w_wind' in merged.columns:
        merged['wind_speed'] = merged['_w_wind'].fillna(
            merged['wind_speed'] if 'wind_speed' in merged.columns else 10.0
        )
        merged.drop(columns=['_w_wind'], inplace=True, errors='ignore')
    elif 'wind_speed' not in merged.columns:
        merged['wind_speed'] = 10.0
    else:
        merged['wind_speed'] = merged['wind_speed'].fillna(10.0)

    return merged


def load_and_enrich_from_mongo(db) -> pd.DataFrame:
    """
    Load all traffic_data and weather_data from MongoDB.
    Labels records as data_source='real' or 'synthetic'.
    Enriches real records with nearest weather observation.
    Returns combined DataFrame sorted by timestamp.
    """
    traffic_records = list(db.traffic_data.find().sort('timestamp', 1))
    weather_records = list(db.weather_data.find().sort('timestamp', 1))

    traffic_df = pd.DataFrame(traffic_records) if traffic_records else pd.DataFrame()
    weather_df = pd.DataFrame(weather_records) if weather_records else pd.DataFrame()

    if traffic_df.empty:
        logger.warning("No traffic records in MongoDB.")
        return traffic_df

    traffic_df['timestamp'] = pd.to_datetime(traffic_df['timestamp'])
    if not weather_df.empty:
        weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'])

    # Label data sources
    SYNTHETIC_SOURCES = {'routeiq_telemetry_engine', 'synthetic_augmentation'}
    if 'source' in traffic_df.columns:
        traffic_df['data_source'] = traffic_df['source'].apply(
            lambda s: 'synthetic' if str(s) in SYNTHETIC_SOURCES else 'real'
        )
    else:
        traffic_df['data_source'] = 'real'

    synth_df = traffic_df[traffic_df['data_source'] == 'synthetic'].copy()
    real_df = traffic_df[traffic_df['data_source'] == 'real'].copy()
    logger.info(f"Data split: {len(real_df)} real, {len(synth_df)} synthetic")

    # Ensure synthetic has weather defaults
    for col, default in [('temperature', 28.0), ('precipitation', 0.0), ('humidity', 65.0), ('wind_speed', 10.0)]:
        if not synth_df.empty:
            if col not in synth_df.columns:
                synth_df[col] = default
            else:
                synth_df[col] = synth_df[col].fillna(default)

    # Enrich real records
    if not real_df.empty:
        real_df = enrich_traffic_with_weather(real_df, weather_df)

    combined_df = pd.concat([synth_df, real_df], ignore_index=True)
    combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
    # Strip timezone info for uniformity
    if hasattr(combined_df['timestamp'], 'dt') and combined_df['timestamp'].dt.tz is not None:
        combined_df['timestamp'] = combined_df['timestamp'].dt.tz_localize(None)
    combined_df = combined_df.sort_values('timestamp').reset_index(drop=True)

    logger.info(f"Enriched combined dataset: {len(combined_df)} records")
    return combined_df


def prepare_segment_series(df: pd.DataFrame, segment_id: str) -> pd.DataFrame:
    """Filter and sort data for a specific road segment."""
    segment_df = df[df['segment_id'] == segment_id].copy()
    if 'timestamp' in segment_df.columns:
        segment_df = segment_df.sort_values('timestamp')
    return segment_df


def get_all_segments(db) -> list:
    """Return segment IDs with at least 20 records."""
    pipeline = [
        {"$group": {"_id": "$segment_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 20}}},
    ]
    results = list(db.traffic_data.aggregate(pipeline))
    return [r['_id'] for r in results if r['_id']]
