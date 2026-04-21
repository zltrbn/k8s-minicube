"""Простое веб-приложение для лабы k8s: health, нагрузка для демо HPA."""
import os
import time

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(
        {
            "service": "my-app",
            "pod": os.environ.get("HOSTNAME", "local"),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/load")
def load():
    duration = min(float(os.environ.get("LOAD_DURATION", "30")), 120)
    end = time.time() + duration
    x = 0
    while time.time() < end:
        x += 1
    return jsonify({"burned": x, "seconds": duration})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
