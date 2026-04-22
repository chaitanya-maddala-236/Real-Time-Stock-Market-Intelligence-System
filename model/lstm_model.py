import json
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

try:
    import tensorflow as tf
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import Dense, LSTM
except Exception:
    tf = None
    Sequential = None
    Dense = None
    LSTM = None


def load_data() -> pd.DataFrame:
    features_path = Path("data/processed/features.csv")
    if not features_path.exists():
        raise FileNotFoundError(
            "Processed features are missing. Run: python spark/process_data.py"
        )
    frame = pd.read_csv(features_path)
    frame = frame.sort_values("event_time").reset_index(drop=True)
    return frame


def build_time_series_sequences(series: np.ndarray, window: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    x, y = [], []
    for i in range(window, len(series)):
        x.append(series[i - window : i])
        y.append(series[i])
    return np.array(x), np.array(y)


def regression_baseline(close_values: np.ndarray) -> Tuple[float, float]:
    n = len(close_values)
    split = max(int(n * 0.8), 2)
    indices = np.arange(n).reshape(-1, 1)

    model = LinearRegression()
    model.fit(indices[:split], close_values[:split])
    preds = model.predict(indices[split:])
    rmse = float(np.sqrt(mean_squared_error(close_values[split:], preds))) if len(preds) > 0 else 0.0
    next_pred = float(model.predict(np.array([[n]]))[0])
    return rmse, next_pred


def lstm_forecast(close_values: np.ndarray, window: int = 10) -> Tuple[float, float]:
    if tf is None or len(close_values) <= window + 5:
        recent = close_values[-window:] if len(close_values) >= window else close_values
        return 0.0, float(np.mean(recent))

    x, y = build_time_series_sequences(close_values, window=window)
    split = max(int(len(x) * 0.8), 1)
    x_train, x_test = x[:split], x[split:]
    y_train, y_test = y[:split], y[split:]

    x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], 1)) if len(x_test) else np.empty((0, window, 1))

    model = Sequential(
        [
            LSTM(32, input_shape=(window, 1)),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse")
    model.fit(x_train, y_train, epochs=15, batch_size=8, verbose=0)

    if len(x_test):
        preds = model.predict(x_test, verbose=0).flatten()
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    else:
        rmse = 0.0

    next_window = close_values[-window:].reshape(1, window, 1)
    next_pred = float(model.predict(next_window, verbose=0).flatten()[0])

    model_artifact_path = Path("model/artifacts/lstm_model.keras")
    model_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(model_artifact_path)

    return rmse, next_pred


def signal_from_prediction(last_close: float, predicted_close: float) -> str:
    change = (predicted_close - last_close) / max(last_close, 1e-9)
    if change > 0.01:
        return "BUY"
    if change < -0.01:
        return "SELL"
    return "HOLD"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main() -> None:
    frame = load_data()
    close_values = frame["close"].astype(float).to_numpy()

    reg_rmse, reg_next = regression_baseline(close_values)
    lstm_rmse, lstm_next = lstm_forecast(close_values, window=10)

    last_close = float(close_values[-1])
    signal = signal_from_prediction(last_close, lstm_next)

    predictions_payload = {
        "last_close": last_close,
        "regression_next_close": reg_next,
        "lstm_next_close": lstm_next,
        "chosen_model": "lstm" if tf is not None else "moving_average_fallback",
    }
    signal_payload = {
        "signal": signal,
        "last_close": last_close,
        "predicted_close": lstm_next,
    }
    metrics_payload = {
        "rmse": {
            "regression": reg_rmse,
            "lstm": lstm_rmse,
        },
        "rows_used": int(len(frame)),
    }

    write_json(Path("data/output/predictions.json"), predictions_payload)
    write_json(Path("data/output/signals.json"), signal_payload)
    write_json(Path("model/artifacts/metrics.json"), metrics_payload)

    print("Training complete. Outputs written to data/output and model/artifacts")


if __name__ == "__main__":
    main()
