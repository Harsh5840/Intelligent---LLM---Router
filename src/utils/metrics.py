"""
Production-grade metrics collection using Prometheus
Tracks routing decisions, model performance, cache efficiency, and cost
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# Create a custom registry for our metrics
REGISTRY = CollectorRegistry()

# ============================================================================
# Routing Metrics
# ============================================================================

routing_decisions_total = Counter(
    "llm_routing_decisions_total",
    "Total routing decisions made",
    ["model_selected", "routing_method", "complexity_tier"],
    registry=REGISTRY,
)

routing_overhead_ms = Histogram(
    "llm_routing_overhead_ms",
    "Time spent in routing decision (excluding model call)",
    buckets=[1, 5, 10, 25, 50, 100, 250, 500],
    registry=REGISTRY,
)

fallback_triggers_total = Counter(
    "llm_fallback_triggers_total",
    "Times routing fell back to secondary model",
    ["primary_model", "fallback_model", "reason"],
    registry=REGISTRY,
)

# ============================================================================
# Model Call Metrics
# ============================================================================

model_call_duration_ms = Histogram(
    "llm_model_call_duration_ms",
    "Model API call duration in milliseconds",
    ["model", "status"],
    buckets=[100, 500, 1000, 2000, 5000, 10000, 30000],
    registry=REGISTRY,
)

model_call_errors_total = Counter(
    "llm_model_call_errors_total",
    "Total model call failures",
    ["model", "error_type"],
    registry=REGISTRY,
)

model_tokens_generated = Histogram(
    "llm_model_tokens_generated",
    "Number of tokens generated per call",
    ["model"],
    buckets=[10, 50, 100, 250, 500, 1000, 2000, 5000],
    registry=REGISTRY,
)

# ============================================================================
# Cache Metrics
# ============================================================================

cache_operations_total = Counter(
    "llm_cache_operations_total",
    "Total cache hits and misses",
    ["operation"],  # 'hit' or 'miss'
    registry=REGISTRY,
)

cache_hit_rate = Gauge(
    "llm_cache_hit_rate",
    "Cache hit rate (0-1)",
    registry=REGISTRY,
)

# ============================================================================
# Circuit Breaker Metrics
# ============================================================================

circuit_breaker_state = Gauge(
    "llm_circuit_breaker_open",
    "Circuit breaker state per model (1=open, 0=closed)",
    ["model"],
    registry=REGISTRY,
)

circuit_breaker_transitions = Counter(
    "llm_circuit_breaker_transitions_total",
    "Total circuit breaker state transitions",
    ["model", "from_state", "to_state"],
    registry=REGISTRY,
)

# ============================================================================
# Cost Metrics
# ============================================================================

cost_estimate_usd_total = Counter(
    "llm_cost_estimate_usd_total",
    "Cumulative estimated inference cost in USD",
    ["model"],
    registry=REGISTRY,
)

# ============================================================================
# Request Metrics (Legacy)
# ============================================================================

REQUEST_COUNT = Counter(
    "llm_router_requests_total",
    "Total number of requests",
    ["model", "endpoint"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "llm_router_request_latency_seconds",
    "Request latency in seconds",
    ["model", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
    registry=REGISTRY,
)

REQUEST_ERRORS = Counter(
    "llm_router_errors_total",
    "Total number of errors",
    ["model", "error_type"],
    registry=REGISTRY,
)

CACHE_HITS = Counter(
    "llm_router_cache_hits_total",
    "Total number of cache hits",
    registry=REGISTRY,
)

CACHE_MISSES = Counter(
    "llm_router_cache_misses_total",
    "Total number of cache misses",
    registry=REGISTRY,
)

ROUTING_DECISIONS = Counter(
    "llm_router_routing_decisions_total",
    "Total routing decisions by type",
    ["routing_type", "model"],
    registry=REGISTRY,
)

ACTIVE_MODELS = Gauge(
    "llm_router_active_models",
    "Number of active models",
    registry=REGISTRY,
)

MODEL_CIRCUIT_BREAKER = Gauge(
    "llm_router_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open)",
    ["model"],
    registry=REGISTRY,
)


def get_metrics() -> tuple[bytes, str]:
    """Get Prometheus metrics in text format"""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST

