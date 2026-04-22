import json
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


BASE_OUTPUT = Path("data/output")
METRICS_PATH = Path("model/artifacts/metrics.json")


def load_json(path: Path):
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/predictions")
def predictions():
    payload = load_json(BASE_OUTPUT / "predictions.json")
    if payload is None:
        return jsonify({"error": "predictions not available"}), 404
    return jsonify(payload)


@app.get("/signals")
def signals():
    payload = load_json(BASE_OUTPUT / "signals.json")
    if payload is None:
        return jsonify({"error": "signals not available"}), 404
    return jsonify(payload)


@app.get("/metrics")
def metrics():
    payload = load_json(METRICS_PATH)
    if payload is None:
        return jsonify({"error": "metrics not available"}), 404
    return jsonify(payload)


@app.get("/latest")
def latest():
    predictions_payload = load_json(BASE_OUTPUT / "predictions.json") or {}
    signal_payload = load_json(BASE_OUTPUT / "signals.json") or {}
    metrics_payload = load_json(METRICS_PATH) or {}

    return jsonify(
        {
            "predictions": predictions_payload,
            "signal": signal_payload,
            "metrics": metrics_payload,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
