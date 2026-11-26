import os
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram,
                               generate_latest)
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "dev")

REQUESTS = Counter(
    "app_requests_total",
    "Nombre total de requetes",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "app_request_duration_seconds",
    "Duree des requetes en secondes",
    ["endpoint"],
)


@app.before_request
def start_timer():
    g.start = time.time()


@app.after_request
def record_metrics(response):
    if request.path != "/metrics":
        LATENCY.labels(request.path).observe(time.time() - g.start)
        REQUESTS.labels(request.method, request.path, response.status_code).inc()
    return response


@app.route("/")
def index():
    return jsonify(message="Bonjour depuis mon pipeline CI/CD", version=VERSION)


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
