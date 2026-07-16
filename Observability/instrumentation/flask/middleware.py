"""
Flask Middleware for Telemetry Injection

Adds distributed tracing context, request IDs, and user/session
attributes to every request passing through the Flask application.
"""

import uuid

from flask import g, request, current_app
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)

tracer = trace.get_tracer(__name__)


def init_telemetry_middleware(app):
    """Register all middleware hooks on the Flask application."""

    @app.before_request
    def inject_trace_context():
        """Add request-scoped trace attributes and correlation IDs."""
        # Generate a unique request ID for log correlation
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.environ["REQUEST_ID"] = g.request_id

        # Extract trace context from incoming headers (if any)
        ctx = TraceContextTextMapPropagator().extract(
            carrier=request.headers,
        )
        if ctx:
            trace.set_span_in_context(ctx)

        # Start a custom span for the full request lifecycle
        span = tracer.start_span(
            name=f"{request.method} {request.path}",
            kind=SpanKind.SERVER,
            attributes={
                "http.request_id": g.request_id,
                "http.method": request.method,
                "http.path": request.path,
                "http.host": request.host,
                "http.user_agent": request.user_agent.string[:256] if request.user_agent else "unknown",
                "http.scheme": request.scheme,
                "http.target": request.full_path[:512],
            },
        )
        g.current_span = span

    @app.after_request
    def finalize_trace(response):
        """Add response attributes and close the request span."""
        span = getattr(g, "current_span", None)
        if span:
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("http.response_size", response.content_length or 0)
            span.set_attribute(
                "http.content_type",
                response.content_type or "unknown",
            )

            # Record errors for 5xx responses
            if response.status_code >= 500:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(
                    Exception(f"HTTP {response.status_code} on {request.method} {request.path}"),
                )
            else:
                span.set_status(Status(StatusCode.OK))

            span.end()

        # Attach trace ID to response headers for debugging
        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            response.headers["X-Trace-ID"] = format(
                span_context.trace_id, "032x"
            )
        response.headers["X-Request-ID"] = getattr(g, "request_id", "unknown")
        return response

    @app.teardown_request
    def cleanup_span_on_error(exc):
        """Ensure span is ended even if an unhandled exception occurs."""
        if exc is not None:
            span = getattr(g, "current_span", None)
            if span and span.is_recording():
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.record_exception(exc)
                span.end()


def get_current_trace_id() -> str:
    """Utility: Get the current trace ID for log correlation."""
    span = trace.get_current_span()
    span_context = span.get_span_context()
    if span_context.is_valid:
        return format(span_context.trace_id, "032x")
    return "00000000000000000000000000000000"
