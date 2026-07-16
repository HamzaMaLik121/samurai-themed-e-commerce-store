"""
Manual Instrumentation Examples for Samurai Shop

This module demonstrates how to add custom business-context spans
alongside the auto-instrumentation provided by OpenTelemetry.

Usage:
    from instrumentation import trace_checkout, trace_database_query
"""

import time
from functools import wraps

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# ── Tracer ──────────────────────────────────────────────────────────────
tracer = trace.get_tracer(__name__)


# ── Decorator: Trace Any Function ──────────────────────────────────────
def trace_call(span_name: str = None, attributes: dict = None):
    """
    Decorator that wraps any function in a custom span.

    Usage:
        @trace_call(span_name="process_order", attributes={"order_id": "123"})
        def process_order(order_id: str):
            ... your logic ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or func.__name__
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator


# ── Context Manager: Manual Span ───────────────────────────────────────
class checkout_span:
    """
    Context manager for tracing checkout operations with business context.

    Usage:
        with checkout_span(order_id="abc123", user_id="user_42"):
            ... checkout logic ...
    """
    def __init__(self, order_id: str = None, user_id: str = None, amount: float = None):
        self.order_id = order_id
        self.user_id = user_id
        self.amount = amount
        self.span = None

    def __enter__(self):
        self.span = tracer.start_span("checkout.process")
        self.span.set_attribute("checkout.order_id", self.order_id or "unknown")
        self.span.set_attribute("checkout.user_id", self.user_id or "unknown")
        if self.amount:
            self.span.set_attribute("checkout.amount", self.amount)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            self.span.record_exception(exc_val)
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()


# ── Business Metric Annotations ────────────────────────────────────────
def record_order_metrics(order_id: str, total: float, items_count: int):
    """Record business-specific metrics as span attributes."""
    with tracer.start_as_current_span("business.order_metrics") as span:
        span.set_attribute("business.order_id", order_id)
        span.set_attribute("business.order_total", total)
        span.set_attribute("business.items_count", items_count)
        span.set_attribute("business.currency", "USD")
        span.add_event("order.completed", {
            "order_id": order_id,
            "total": total,
            "timestamp": time.time_ns()
        })


def record_cart_abandonment(cart_id: str, items_count: int, total_value: float):
    """Track cart abandonment with business context."""
    with tracer.start_as_current_span("business.cart_abandoned") as span:
        span.set_attribute("business.cart_id", cart_id)
        span.set_attribute("business.items_count", items_count)
        span.set_attribute("business.total_value", total_value)
        span.set_attribute("business.abandonment_reason", "session_timeout")


# ── Caching Operations ─────────────────────────────────────────────────
class cache_tracker:
    """
    Track cache hit/miss ratio for database queries.

    Usage:
        cache = cache_tracker()
        if cache.is_hit("city_list"):
            result = cache.get("city_list")
        else:
            result = query_database()
            cache.set("city_list", result)
    """
    def __init__(self):
        self._hits = 0
        self._misses = 0

    def is_hit(self, key: str) -> bool:
        with tracer.start_as_current_span("cache.check") as span:
            hit = self._hits > self._misses  # Simplified example
            span.set_attribute("cache.key", key)
            span.set_attribute("cache.hit", hit)
            return hit

    def get(self, key: str):
        """Simulate cache get with span."""
        with tracer.start_as_current_span("cache.get") as span:
            span.set_attribute("cache.key", key)
            # Actual Redis/memcached get here
            return None

    def set(self, key: str, value):
        """Simulate cache set with span."""
        with tracer.start_as_current_span("cache.set") as span:
            span.set_attribute("cache.key", key)
            span.set_attribute("cache.size_bytes", len(str(value)))
            # Actual Redis/memcached set here
