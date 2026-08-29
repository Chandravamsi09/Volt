"""
Volt Metrics & Structured Telemetry Module
"""

import logging
import sys
import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("volt")

# Prometheus Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "volt_http_requests_total",
    "Total HTTP Requests handled by Volt API",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "volt_http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

INFERENCE_REQUESTS_TOTAL = Counter(
    "volt_inference_requests_total",
    "Total real-time model inference requests",
    ["model_id", "version", "status"],
)

INFERENCE_LATENCY_SECONDS = Histogram(
    "volt_inference_latency_seconds",
    "Inference latency in seconds",
    ["model_id", "version"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1.0],
)

FEATURE_STORE_READ_TOTAL = Counter(
    "volt_feature_store_read_total",
    "Feature Store read queries",
    ["store_type", "status"],
)


async def prometheus_metrics_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for tracking HTTP metrics with Prometheus."""
    start_time = time.perf_counter()
    endpoint = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        status_code = str(response.status_code)
    except Exception as exc:
        status_code = "500"
        logger.error(f"Unhandled error in request {method} {endpoint}: {exc}")
        raise
    finally:
        duration = time.perf_counter() - start_time
        # Avoid exploding metric cardinality for parameterized paths
        if not endpoint.startswith("/metrics"):
            HTTP_REQUESTS_TOTAL.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method, endpoint=endpoint
            ).observe(duration)

    return response
