"""
ml/patchtst/training.py — Improved PatchTST Training Pipeline.

Key improvements over v1:
- 70/15/15 chronological train/val/test split (no shuffle of time-series)
- 12-feature enriched input
- Separate validation set for early stopping
- AdamW optimizer with weight_decay
- Metrics computed in original units (speed km/h, travel time seconds)
- Baseline comparison (HistoricalAverageBaseline)
- Model versioning via model_registry
- No data leakage: test set is untouched until final evaluation
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import json
import datetime
from pathlib import Path
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from loguru import logger

from ml.patchtst.config import PatchTSTConfig
from ml.patchtst.dataset import TrafficDataset, load_training_data
from ml.patchtst.model import PatchTST
from ml.patchtst.preprocessing import (
    FEATURE_COLUMNS_ENRICHED, TARGET_COLUMNS,
    build_feature_matrix, chronological_split
)
from ml.patchtst.baseline import HistoricalAverageBaseline, compute_metrics
from ml.patchtst.model_registry import (
    register_model, get_active_version, get_version_info,
    should_promote, promote_model
)


def train_patchtst(db):
    """
    Main training function. Triggered by Admin from dashboard.
    Returns metrics dict.
    """
    config = PatchTSTConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Training PatchTST {config.model_version} on {device}")

    # ── 1. Load & prepare data ────────────────────────────────────────────────
    raw_df, real_count, synth_count, date_range = load_training_data(db)
    logger.info(f"Dataset: {len(raw_df)} records ({real_count} real, {synth_count} synthetic)")
    logger.info(f"Date range: {date_range['start']} → {date_range['end']}")

    # Build enriched feature matrix
    feature_df = build_feature_matrix(raw_df)

    # Available features (only those in feature_df)
    available_features = [c for c in FEATURE_COLUMNS_ENRICHED if c in feature_df.columns]
    num_features = len(available_features)
    logger.info(f"Features used ({num_features}): {available_features}")

    # Identify target column indices within available_features
    target_col_indices = [available_features.index(c) for c in ['speed_kmh', 'current_travel_time', 'tci'] if c in available_features]
    if not target_col_indices:
        target_col_indices = [0]  # fallback
    n_targets = len(target_col_indices)
    logger.info(f"Target indices: {target_col_indices}")

    # ── 2. Chronological 70/15/15 split ───────────────────────────────────────
    # IMPORTANT: Never shuffle time series data before splitting
    train_df, val_df, test_df = chronological_split(feature_df, train_pct=config.train_pct, val_pct=config.val_pct)
    logger.info(f"Split: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

    if len(train_df) < config.context_length + config.forecast_horizon:
        logger.error("Insufficient data for training. Need more records.")
        return {"status": "error", "message": "Insufficient training data"}

    # ── 3. Fit scaler on TRAINING DATA ONLY (prevents data leakage) ───────────
    train_values = train_df[available_features].values.astype(np.float32)
    scaler = StandardScaler()
    scaler.fit(train_values)
    with open(config.scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    # Backward-compat tuple format
    mean_arr = scaler.mean_.astype(np.float32)
    std_arr = np.sqrt(scaler.var_).astype(np.float32)
    std_arr[std_arr < 0.1] = 0.1  # safe minimum
    with open(config.legacy_scaler_path, "wb") as f:
        pickle.dump((mean_arr, std_arr), f)

    # Scale all splits using training scaler
    train_scaled = scaler.transform(train_values)
    val_values = val_df[available_features].values.astype(np.float32)
    val_scaled = scaler.transform(val_values)
    test_values = test_df[available_features].values.astype(np.float32)
    test_scaled = scaler.transform(test_values)

    # ── 4. Baseline evaluation on test set (before training) ─────────────────
    baseline = HistoricalAverageBaseline()
    # If timestamp is available in raw_df, use it for baseline
    if 'timestamp' in raw_df.columns:
        train_raw_vals = train_df['speed_kmh'].values if 'speed_kmh' in train_df.columns else train_values[:, 0]
        test_raw_vals = test_df['speed_kmh'].values if 'speed_kmh' in test_df.columns else test_values[:, 0]
        baseline.fit(train_df, feature_col='speed_kmh')
        baseline_metrics = baseline.evaluate(test_df, feature_col='speed_kmh')
    else:
        # Simple global mean as baseline
        train_mean = float(np.nanmean(train_values[:, 0]))
        test_true = test_values[:, 0]
        pred_baseline = np.full_like(test_true, train_mean)
        baseline_metrics = compute_metrics(test_true, pred_baseline, label='HistoricalMean')
    logger.info(f"Baseline (HistAvg) — MAE={baseline_metrics['mae']:.3f}, RMSE={baseline_metrics['rmse']:.3f}, MAPE={baseline_metrics['mape']:.2f}%")

    # ── 5. Create Datasets ────────────────────────────────────────────────────
    train_dataset = TrafficDataset(train_scaled, config, target_indices=target_col_indices)
    val_dataset = TrafficDataset(val_scaled, config, target_indices=target_col_indices)
    test_dataset = TrafficDataset(test_scaled, config, target_indices=target_col_indices)

    if len(train_dataset) == 0:
        return {"status": "error", "message": "No training windows created. Reduce context_length or get more data."}

    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)

    # ── 6. Initialize model ───────────────────────────────────────────────────
    model = PatchTST(config, num_features).to(device)
    huber_loss = nn.SmoothL1Loss(beta=0.5)
    l1_loss = nn.L1Loss()
    def loss_fn(pred, true):
        return huber_loss(pred, true) + 0.2 * l1_loss(pred, true)

    optimizer = optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs, eta_min=1e-6)

    # ── 7. Training loop with early stopping on VAL loss ─────────────────────
    best_val_loss = float("inf")
    patience_counter = 0
    train_losses = []
    val_losses = []

    for epoch in range(config.epochs):
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)  # [B, pred_len, num_features]
            # Slice to target features only
            out_targets = out[:, :, :n_targets] if out.shape[2] >= n_targets else out
            loss = loss_fn(out_targets, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item() * x.size(0)

        train_loss /= max(len(train_loader.dataset), 1)
        train_losses.append(train_loss)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                out = model(x)
                out_targets = out[:, :, :n_targets] if out.shape[2] >= n_targets else out
                val_loss += loss_fn(out_targets, y).item() * x.size(0)

        val_loss /= max(len(val_loader.dataset), 1)
        val_losses.append(val_loss)
        scheduler.step()

        logger.info(f"Epoch {epoch+1}/{config.epochs} — Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), config.model_path)
            logger.info(f"  ✓ New best val loss: {best_val_loss:.4f} — checkpoint saved")
        else:
            patience_counter += 1
            if patience_counter >= config.patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break

    # ── 8. Final evaluation on UNTOUCHED test set ─────────────────────────────
    model.load_state_dict(torch.load(config.model_path, map_location=device))
    model.eval()

    all_preds = []
    all_targets = []
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(device)
            out = model(x)
            out_targets = out[:, :, :n_targets] if out.shape[2] >= n_targets else out
            all_preds.append(out_targets.cpu().numpy())
            all_targets.append(y.numpy())

    if all_preds:
        preds_scaled = np.concatenate(all_preds, axis=0)  # [N, pred_len, n_targets]
        targets_scaled = np.concatenate(all_targets, axis=0)

        # Inverse transform: use scaler mean/std for target columns only
        target_means = scaler.mean_[target_col_indices]
        target_stds = np.sqrt(scaler.var_)[target_col_indices]
        target_stds[target_stds < 0.1] = 0.1

        # Flatten pred_len dimension to compute metrics per target
        B, L, T = preds_scaled.shape
        preds_unscaled = preds_scaled.reshape(-1, T) * target_stds + target_means
        targets_unscaled = targets_scaled.reshape(-1, T) * target_stds + target_means

        # Per-variable metrics
        target_names = ['speed_kmh', 'current_travel_time', 'tci'][:T]
        per_var_metrics = {}
        for ti, tname in enumerate(target_names):
            pm = compute_metrics(targets_unscaled[:, ti], preds_unscaled[:, ti], label=tname)
            per_var_metrics[tname] = pm
            logger.info(f"  Test {tname}: MAE={pm['mae']:.3f}, RMSE={pm['rmse']:.3f}, MAPE={pm['mape']:.2f}%")

        # Overall metrics (speed as primary)
        primary = per_var_metrics.get('speed_kmh', list(per_var_metrics.values())[0])
        overall_mae = primary['mae']
        overall_rmse = primary['rmse']
        overall_mape = primary['mape']
        derived_accuracy = primary['derived_accuracy']
    else:
        overall_mae = overall_rmse = overall_mape = derived_accuracy = 0.0
        per_var_metrics = {}

    # ── 9. Build and save metrics ──────────────────────────────────────────────
    metrics = {
        "status": "success",
        "timestamp": datetime.datetime.now().isoformat(),
        "model_version": config.model_version,
        # Overall metrics (speed km/h)
        "mae": round(float(overall_mae), 4),
        "rmse": round(float(overall_rmse), 4),
        "mape": round(float(overall_mape), 4),
        "derived_accuracy_score": round(float(derived_accuracy), 2),
        # Per-variable metrics
        "per_variable": {k: {kk: round(float(vv), 4) for kk, vv in v.items() if isinstance(vv, float)} for k, v in per_var_metrics.items()},
        # Baseline comparison
        "baseline": {
            "type": "HistoricalAverageBaseline",
            "mae": round(float(baseline_metrics['mae']), 4),
            "rmse": round(float(baseline_metrics['rmse']), 4),
            "mape": round(float(baseline_metrics['mape']), 4),
        },
        # Data provenance
        "dataset": {
            "total_records": len(raw_df),
            "real_records": int(real_count),
            "synthetic_records": int(synth_count),
            "date_range_start": date_range['start'],
            "date_range_end": date_range['end'],
            "train_records": len(train_df),
            "val_records": len(val_df),
            "test_records": len(test_df),
        },
        # Architecture
        "architecture": {
            "context_length": config.context_length,
            "forecast_horizon": config.forecast_horizon,
            "patch_length": config.patch_length,
            "patch_stride": config.patch_stride,
            "d_model": config.d_model,
            "n_heads": config.n_heads,
            "n_encoder_layers": config.n_encoder_layers,
            "dropout": config.dropout,
            "num_features": num_features,
            "num_target_features": n_targets,
        },
        # Training history
        "training": {
            "epochs_run": len(train_losses),
            "best_val_loss": round(float(best_val_loss), 6),
            "learning_rate": config.learning_rate,
            "weight_decay": config.weight_decay,
            "batch_size": config.batch_size,
        },
        "features_used": available_features,
    }

    with open(config.metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {config.metrics_path}")

    # ── 10. Register model version ─────────────────────────────────────────────
    try:
        val_metrics_for_reg = {"mae": float(best_val_loss), "val_mse": float(best_val_loss)}
        test_metrics_for_reg = {"mae": float(overall_mae), "rmse": float(overall_rmse), "mape": float(overall_mape)}
        current_active = get_active_version()
        current_info = get_version_info(current_active) if current_active else None
        current_val = current_info.get('val_metrics') if current_info else None

        register_model(
            version=config.model_version,
            config_dict=metrics["architecture"],
            train_metrics={"final_train_loss": round(train_losses[-1], 6) if train_losses else 0.0},
            val_metrics=val_metrics_for_reg,
            test_metrics=test_metrics_for_reg,
            checkpoint_path=str(config.model_path),
            train_date_range=date_range,
            features_used=available_features,
        )
        if should_promote(val_metrics_for_reg, current_val):
            promote_model(config.model_version)
            logger.info(f"Promoted {config.model_version} to active model.")
    except Exception as reg_err:
        logger.warning(f"Model registry update failed (non-fatal): {reg_err}")

    logger.info(f"PatchTST training complete. MAE={overall_mae:.3f} km/h, Baseline MAE={baseline_metrics['mae']:.3f} km/h")
    return metrics
