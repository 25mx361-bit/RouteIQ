# Phase 12: PatchTST — ML Training & Inference

This plan covers the implementation of the PatchTST time-series forecasting model for RouteIQ, including the model architecture, data pipelines, and backend triggers.

## Proposed Changes

### Machine Learning Module (`ml/patchtst/`)

#### [NEW] `ml/patchtst/config.py`
- Configuration class `PatchTSTConfig` defining all hyperparameters (context length, patch length, model dimensions, heads, layers, dropout, batch size, learning rate).

#### [NEW] `ml/patchtst/preprocessing.py`
- Functions to clean and merge raw traffic and weather data from MongoDB.
- Handles missing value imputation, sorting by time, and feature extraction (e.g., hour of day, day of week).

#### [NEW] `ml/patchtst/dataset.py`
- PyTorch `Dataset` implementation (`TrafficDataset`).
- Creates rolling windows (context window -> forecast horizon).
- Applies `StandardScaler` (saved via `joblib` for inference).

#### [NEW] `ml/patchtst/model.py`
- PyTorch implementation of the **PatchTST** (Patch Time Series Transformer) architecture.
- Handles patching of input sequences, positional encodings, Transformer Encoder layers, and the linear prediction head.

#### [NEW] `ml/patchtst/training.py`
- Training loop implementation (`train_patchtst`).
- Chronological train/validation splitting.
- Uses MSE loss, Adam optimizer.
- Saves best model checkpoints to `ml/patchtst/checkpoints/` and logs metrics to MongoDB or a local log file.

#### [NEW] `ml/patchtst/evaluation.py`
- Functions to calculate and log MAE, RMSE, MAPE on the test set/validation set.

#### [NEW] `ml/patchtst/prediction.py`
- Inference wrapper `predict_traffic`.
- Loads the best checkpoint and scaler.
- Formats recent inputs and returns predictions (speed, travel_time, flow) for routes.

### Backend Endpoints

#### [MODIFY] `backend/routes/admin_routes.py` & `backend/controllers/admin_controller.py`
- `POST /api/admin/models/patchtst/train`: Admin endpoint that triggers the `train_patchtst` function in a background thread.
- `GET /api/admin/models/patchtst/metrics`: Returns the latest evaluation metrics (MAE, RMSE, MAPE, etc.) from the model logs.

## Verification Plan

### Automated/Unit Tests
- Basic shape testing of the `TrafficDataset` output.
- Forward pass validation of the `PatchTST` PyTorch model (verify `output.shape == (batch, target_vars, forecast_horizon)`).
- Test admin trigger API endpoints.

### Manual Verification
- Trigger training via POST endpoint and ensure it runs non-blocking.
- Verify metrics JSON response from the GET endpoint.
