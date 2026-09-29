import pandas as pd
import numpy as np

class HistoricalAverageBaseline:
    def fit(self, df: pd.DataFrame, feature_col='speed_kmh'):
        self.feature_col = feature_col
        df_temp = df.copy()
        if 'timestamp' in df_temp.columns:
            df_temp['day_of_week'] = df_temp['timestamp'].dt.dayofweek
            df_temp['hour'] = df_temp['timestamp'].dt.hour
        else:
            df_temp['day_of_week'] = 0
            df_temp['hour'] = 0
        self.lookup_table = df_temp.groupby(['day_of_week', 'hour'])[feature_col].mean().to_dict()
        self.global_mean = df_temp[feature_col].mean()

    def predict(self, timestamps: list) -> list:
        preds = []
        for ts in timestamps:
            if hasattr(ts, 'dayofweek'):
                dow = ts.dayofweek
                hr = ts.hour
            else:
                dow = 0
                hr = 0
            pred = self.lookup_table.get((dow, hr), self.global_mean)
            preds.append(pred)
        return preds

    def evaluate(self, df_test: pd.DataFrame, feature_col='speed_kmh') -> dict:
        timestamps = df_test['timestamp'].tolist() if 'timestamp' in df_test.columns else df_test.index.tolist()
        y_pred = np.array(self.predict(timestamps))
        y_true = df_test[feature_col].values
        return compute_metrics(y_true, y_pred, label='HistoricalAverage')

class MovingAverageBaseline:
    def __init__(self, window=4):
        self.window = window

    def fit(self, df: pd.DataFrame, feature_col='speed_kmh'):
        self.train_series = df[feature_col].values.tolist()

    def predict_next(self, n: int) -> list:
        if not self.train_series:
            return [0.0] * n
        recent = self.train_series[-self.window:]
        avg = sum(recent) / len(recent) if recent else 0.0
        return [avg] * n

    def evaluate(self, df_train: pd.DataFrame, df_test: pd.DataFrame, feature_col='speed_kmh') -> dict:
        train_vals = df_train[feature_col].tolist()
        test_vals = df_test[feature_col].tolist()
        full_series = train_vals + test_vals
        train_len = len(train_vals)
        preds = []
        for i in range(len(test_vals)):
            idx = train_len + i
            recent = full_series[max(0, idx - self.window):idx]
            avg = sum(recent) / len(recent) if recent else 0.0
            preds.append(avg)
        y_true = np.array(test_vals)
        y_pred = np.array(preds)
        return compute_metrics(y_true, y_pred, label='MovingAverage')

def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, label='') -> dict:
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    mape = np.mean(np.abs(y_true - y_pred) / (np.abs(y_true) + 1e-8)) * 100
    derived_accuracy = max(0.0, 100.0 - mape)
    return {
        "label": label,
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
        "derived_accuracy": float(derived_accuracy),
        "n_samples": len(y_true)
    }
