import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import yfinance as yf

try:
    from kafka import KafkaProducer
except Exception:
    KafkaProducer = None


def fetch_latest_tick(ticker: str) -> dict:
    frame = yf.Ticker(ticker).history(period="1d", interval="1m")
    if frame.empty:
        raise ValueError(f"No data returned for ticker '{ticker}'")

    row = frame.iloc[-1]
    index = frame.index[-1]
    event_time = index.to_pydatetime() if hasattr(index, "to_pydatetime") else datetime.now(timezone.utc)

    return {
        "ticker": ticker.upper(),
        "event_time": event_time.astimezone(timezone.utc).isoformat(),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": float(row.get("Volume", 0.0)),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }


def build_producer(bootstrap_servers: str):
    if KafkaProducer is None:
        return None
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def append_local(payload: dict, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce real-time stock ticks to Kafka/local")
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--topic", default="stock_ticks")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--max-messages", type=int, default=30)
    parser.add_argument("--local-output", default="data/raw/stream_ticks.jsonl")
    args = parser.parse_args()

    producer = None
    try:
        producer = build_producer(args.bootstrap_servers)
    except Exception as ex:
        print(f"Kafka unavailable, using local output only: {ex}")

    output_file = Path(args.local_output)
    print(f"Producing {args.max_messages} ticks for {args.ticker}...")

    for _ in range(args.max_messages):
        payload = fetch_latest_tick(args.ticker)
        append_local(payload, output_file)

        if producer is not None:
            try:
                producer.send(args.topic, value=payload)
                producer.flush()
            except Exception as ex:
                print(f"Kafka send failed, continuing with local write: {ex}")

        print(f"Published tick: {payload['ticker']} @ {payload['close']:.2f}")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
