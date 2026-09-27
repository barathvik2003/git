from flask import Flask, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total number of HTTP requests"
)

ERROR_COUNT = Counter(
    "app_http_errors_total",
    "Total number of HTTP errors"
)


@app.before_request
def count_request():
    REQUEST_COUNT.inc()


@app.route("/")
def home():
    return "Company Management Application"


@app.route("/health")
def health():
    return "OK"


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


@app.errorhandler(404)
def not_found(error):
    ERROR_COUNT.inc()
    return "Not Found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
