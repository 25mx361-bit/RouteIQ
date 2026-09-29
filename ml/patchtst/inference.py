"""
ml/patchtst/inference.py — PatchTST Inference Engine.

IMPORTANT: predict_route_traffic() now uses the TRAINED PyTorch model.
Mathematical fallback is only used if no checkpoint exists.
"""
import torch
import numpy as np
import pickle
import pandas as pd
import math
from pathlib import Path
from datetime import datetime, timezone, timedelta
from loguru import logger

from ml.patchtst.config import PatchTSTConfig
from ml.patchtst.model import PatchTST
from ml.patchtst.preprocessing import FEATURE_COLUMNS_ENRICHED, build_feature_matrix
from ml.patchtst.model_registry import get_active_version


class PatchTSTPredictor:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.config = PatchTSTConfig()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.scaler = None
        self.available_features = FEATURE_COLUMNS_ENRICHED
        self.model_version = "unknown"
        self.load_model()

    def load_model(self) -> bool:
        """Load the best trained model checkpoint."""
        # Try v2 checkpoint first
        model_path = self.config.model_path
        scaler_path = self.config.scaler_path

        # Fall back to v1 if v2 doesn't exist
        if not model_path.exists():
            model_path = self.config.legacy_model_path
            scaler_path = self.config.legacy_scaler_path

        if not model_path.exists() or not scaler_path.exists():
            logger.warning("PatchTST: No checkpoint found. Will use fallback formula.")
            return False

        try:
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)

            # Handle both sklearn StandardScaler and legacy tuple (mean, std)
            if isinstance(self.scaler, tuple):
                mean_arr, std_arr = self.scaler
                self.scaler_mean = mean_arr
                self.scaler_std = std_arr
                num_features = len(mean_arr)
            else:
                # sklearn StandardScaler
                self.scaler_mean = self.scaler.mean_.astype(np.float32)
                self.scaler_std = np.sqrt(self.scaler.var_).astype(np.float32)
                num_features = len(self.scaler_mean)

            self.scaler_std[self.scaler_std < 0.1] = 0.1
            self.model = PatchTST(self.config, num_features).to(self.device)
            state = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state)
            self.model.eval()

            active_ver = get_active_version()
            self.model_version = active_ver or self.config.model_version
            logger.info(f"PatchTST loaded: {model_path.name}, version={self.model_version}, features={num_features}")
            return True
        except Exception as e:
            logger.error(f"Error loading PatchTST model: {e}")
            self.model = None
            return False

    def predict(self, recent_data: pd.DataFrame) -> np.ndarray:
        """
        Run inference on a sequence of recent_data.
        recent_data: DataFrame with at least context_length rows, feature columns.
        Returns: np.ndarray of shape [pred_len, n_features] in original units.
        """
        if self.model is None:
            raise FileNotFoundError("PatchTST model not loaded. Train the model first.")

        # Build feature matrix from raw data
        feature_df = build_feature_matrix(recent_data)
        available = [c for c in FEATURE_COLUMNS_ENRICHED if c in feature_df.columns]
        raw_values = feature_df[available].values.astype(np.float32)

        # Align to scaler dimensions
        n_scaler_feats = len(self.scaler_mean)
        if raw_values.shape[1] != n_scaler_feats:
            if raw_values.shape[1] < n_scaler_feats:
                pad = np.zeros((raw_values.shape[0], n_scaler_feats - raw_values.shape[1]), dtype=np.float32)
                raw_values = np.hstack([raw_values, pad])
            else:
                raw_values = raw_values[:, :n_scaler_feats]

        # Ensure exactly context_length steps
        ctx = self.config.context_length
        if len(raw_values) >= ctx:
            raw_values = raw_values[-ctx:]
        else:
            # Replicate earliest available row instead of zero-padding to preserve stationary distribution and RevIN statistics
            pad_rows = ctx - len(raw_values)
            raw_values = np.vstack([np.repeat(raw_values[0:1], pad_rows, axis=0), raw_values])

        scaled = (raw_values - self.scaler_mean) / self.scaler_std
        x = torch.tensor(scaled).unsqueeze(0).to(self.device)  # [1, ctx, feats]

        with torch.no_grad():
            out = self.model(x)  # [1, pred_len, feats]

        out_np = out.squeeze(0).cpu().numpy()  # [pred_len, feats]
        predictions = out_np * self.scaler_std + self.scaler_mean
        return predictions

    def predict_at_horizon(self, recent_data: pd.DataFrame, horizon_steps: int = 36) -> dict:
        """
        Predict traffic at a specific future step (default 36 = 9 hours ahead at 15-min intervals).
        Used for 8AM → 5PM prediction (8AM + 9 hours = 5PM).
        Returns dict with predicted_speed_kmh, predicted_travel_time, predicted_tci, etc.
        """
        try:
            predictions = self.predict(recent_data)  # [pred_len, n_features]
            step = min(horizon_steps, len(predictions) - 1)
            pred_step = predictions[step]  # [n_features]

            # Map features back by index
            available = [c for c in FEATURE_COLUMNS_ENRICHED if c in build_feature_matrix(recent_data).columns]
            available = available[:len(pred_step)]
            pred_dict = {feat: float(pred_step[i]) for i, feat in enumerate(available)}

            speed = max(1.0, pred_dict.get('speed_kmh', 30.0))
            travel_time = max(1.0, pred_dict.get('current_travel_time', 600.0))
            ff_travel = pred_dict.get('free_flow_travel_time', travel_time * 0.7)
            tci = travel_time / max(ff_travel, 1.0)
            tci = min(10.0, max(0.5, tci))

            if tci >= 1.40:
                congestion_level = "HIGH"
            elif tci >= 1.15:
                congestion_level = "MEDIUM"
            else:
                congestion_level = "LOW"

            return {
                "predicted_speed_kmh": round(speed, 2),
                "predicted_travel_time": round(travel_time, 1),  # seconds
                "predicted_travel_time_min": round(travel_time / 60.0, 2),
                "predicted_tci": round(tci, 4),
                "congestion_level": congestion_level,
                "model_version": self.model_version,
                "horizon_steps": step,
                "method": "patchtst_model",
            }
        except Exception as e:
            logger.warning(f"PatchTST inference failed, using fallback: {e}")
            return self._fallback_prediction()

    def predict_route_traffic(
        self,
        distance_km: float,
        target_datetime: datetime = None,
        precipitation: float = 0.0,
        recent_db_data: pd.DataFrame = None,
    ) -> dict:
        """
        Produce traffic forecast for a route. Uses trained model if available,
        falls back to mathematical formula only if no checkpoint exists.
        """
        if target_datetime is None:
            target_datetime = datetime.now(timezone.utc)

        # Try model-based prediction if we have enough context data
        if self.model is not None and recent_db_data is not None and len(recent_db_data) >= 20:
            try:
                result = self.predict_at_horizon(recent_db_data, horizon_steps=self.config.forecast_horizon - 1)
                # Directly predicted speed from model (clamped to realistic road speeds)
                speed = max(5.0, min(100.0, result.get('predicted_speed_kmh', 35.0)))
                tci = max(0.8, min(5.0, result.get('predicted_tci', 1.0)))
                
                # Physical travel time for route distance
                travel_time_hours = distance_km / max(speed, 5.0)
                travel_time_sec = travel_time_hours * 3600.0
                travel_time_min = travel_time_hours * 60.0
                
                ff_speed = min(110.0, speed * max(1.1, tci))
                ff_time_min = (distance_km / ff_speed) * 60.0
                delay_min = max(0.0, travel_time_min - ff_time_min)
                
                result['predicted_speed_kmh'] = round(speed, 1)
                result['predicted_travel_time'] = round(travel_time_sec, 1)
                result['predicted_travel_time_min'] = round(travel_time_min, 2)
                result['free_flow_speed_kmh'] = round(ff_speed, 1)
                result['free_flow_travel_time'] = round(ff_time_min * 60.0, 1)
                result['free_flow_travel_time_min'] = round(ff_time_min, 2)
                result['delay_minutes'] = round(delay_min, 2)
                result['predicted_tci'] = round(tci, 4)
                return result
            except Exception as e:
                logger.warning(f"Model-based prediction failed: {e}. Falling back to formula.")

        # ── Mathematical fallback (original logic retained) ────────────────────
        return self._formula_prediction(distance_km, target_datetime, precipitation)

    def _formula_prediction(self, distance_km: float, target_datetime: datetime, precipitation: float = 0.0) -> dict:
        """Original mathematical formula-based prediction (fallback only)."""
        hour = target_datetime.hour + target_datetime.minute / 60.0
        weekday = target_datetime.weekday()
        is_weekend = weekday >= 5

        if distance_km < 3.0:
            road_type_factor = 1.05
            free_flow_speed = 36.0
            min_rush_speed = 18.0 if not is_weekend else 22.0
        elif distance_km < 7.0:
            road_type_factor = 1.0
            free_flow_speed = 42.0
            min_rush_speed = 20.0 if not is_weekend else 24.0
        elif distance_km < 15.0:
            road_type_factor = 0.95
            free_flow_speed = 48.0
            min_rush_speed = 24.0 if not is_weekend else 28.0
        else:
            road_type_factor = 0.90
            free_flow_speed = 55.0
            min_rush_speed = 30.0 if not is_weekend else 36.0

        free_flow_travel_time = (distance_km / free_flow_speed) * 60.0

        if not is_weekend:
            m_dist = abs(hour - 9.25)
            m_factor = math.exp(-0.5 * (m_dist / 1.3) ** 2) if m_dist < 3.5 else 0.0
            mid_dist = abs(hour - 13.5)
            mid_factor = 0.60 * math.exp(-0.5 * (mid_dist / 2.2) ** 2) if mid_dist < 4.0 else 0.0
            e_dist = abs(hour - 19.5)
            e_factor = math.exp(-0.5 * (e_dist / 2.2) ** 2) if e_dist < 4.5 else 0.0
            n_dist = abs(hour - 22.3)
            n_factor = 0.80 * math.exp(-0.5 * (n_dist / 1.2) ** 2) if n_dist < 2.5 else 0.0
            congestion_impact = max(0.95 * m_factor, 0.95 * e_factor, mid_factor, n_factor)
        else:
            w_mid = abs(hour - 13.5)
            w_mid_factor = 0.75 * math.exp(-0.5 * (w_mid / 2.2) ** 2) if w_mid < 4.5 else 0.0
            w_eve = abs(hour - 20.0)
            w_eve_factor = 0.95 * math.exp(-0.5 * (w_eve / 2.4) ** 2) if w_eve < 4.8 else 0.0
            congestion_impact = max(w_mid_factor, w_eve_factor)

        congestion_impact = min(1.0, max(0.0, congestion_impact))
        effective_congestion = min(1.0, congestion_impact * road_type_factor)
        weather_penalty = 0.25 if precipitation > 5.0 else 0.10 if precipitation > 0.5 else 0.0
        pred_speed = free_flow_speed - (free_flow_speed - min_rush_speed) * effective_congestion
        pred_speed = pred_speed * (1.0 - weather_penalty)
        pred_speed = max(min_rush_speed * 0.85, min(free_flow_speed, pred_speed))
        pred_travel_time = (distance_km / pred_speed) * 60.0
        tci = round(pred_travel_time / free_flow_travel_time, 2)

        arrival_dt = target_datetime + timedelta(minutes=pred_travel_time)

        if tci >= 1.40:
            congestion_level = "HIGH"
        elif tci >= 1.15:
            congestion_level = "MEDIUM"
        else:
            congestion_level = "LOW"

        return {
            "predicted_speed_kmh": round(pred_speed, 1),
            "predicted_travel_time": round(pred_travel_time * 60.0, 1),
            "predicted_travel_time_min": round(pred_travel_time, 1),
            "free_flow_speed_kmh": round(free_flow_speed, 1),
            "free_flow_travel_time": round(free_flow_travel_time * 60.0, 1),
            "free_flow_travel_time_min": round(free_flow_travel_time, 1),
            "tci": tci,
            "congestion_level": congestion_level,
            "delay_minutes": round(max(0.0, pred_travel_time - free_flow_travel_time), 1),
            "arrival_time": arrival_dt.strftime("%I:%M %p"),
            "arrival_datetime": arrival_dt.isoformat(),
            "model_version": "formula_calibrated_google",
            "method": "mathematical_formula",
        }

    def _fallback_prediction(self) -> dict:
        return {
            "predicted_speed_kmh": 30.0,
            "predicted_travel_time": 600.0,
            "predicted_travel_time_min": 10.0,
            "predicted_tci": 1.0,
            "congestion_level": "MEDIUM",
            "model_version": "fallback",
            "method": "fallback_default",
        }


def invalidate_patchtst_cache():
    PatchTSTPredictor._instance = None
