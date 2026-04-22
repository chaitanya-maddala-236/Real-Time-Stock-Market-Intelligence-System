import json
from pathlib import Path

import pandas as pd


def load_ticks(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Tick file not found: {path}")

    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    if not records:
        raise ValueError("No tick records found to process")

    frame = pd.DataFrame(records)
    frame["event_time"] = pd.to_datetime(frame["event_time"], utc=True, errors="coerce")
    frame = frame.sort_values("event_time").dropna(subset=["close"])
    return frame


def generate_features(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["return_1"] = frame["close"].pct_change()
    frame["sma_3"] = frame["close"].rolling(window=3).mean()
    frame["sma_5"] = frame["close"].rolling(window=5).mean()
    frame["ema_5"] = frame["close"].ewm(span=5, adjust=False).mean()
    frame["target_next_close"] = frame["close"].shift(-1)
    frame = frame.dropna().reset_index(drop=True)
    return frame


def main() -> None:
    input_path = Path("data/raw/consumed_ticks.jsonl")
    output_path = Path("data/processed/features.csv")

    frame = load_ticks(input_path)
    features = generate_features(frame)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)
    print(f"Saved processed features: {output_path} ({len(features)} rows)")


if __name__ == "__main__":
    main()
