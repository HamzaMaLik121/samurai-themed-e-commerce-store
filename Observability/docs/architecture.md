# Architecture Deep Dive

## Design Principles

This observability stack follows three core principles:

1. **Vendor-Neutral Instrumentation** — All telemetry is generated using the OpenTelemetry SDK. This means you can swap the backend (Jaeger, Tempo, X-Ray, Datadog) with zero application code changes.
2. **Unified Pipeline** — A single OpenTelemetry Collector receives all signals (traces, metrics, logs) and routes them to the appropriate backends. This reduces the number of agents running on each host.
3. **Correlation by Design** — Traces, metrics, and logs are linked through shared identifiers (`trace_id`, `service.name`), enabling drill-downs from dashboards to traces to logs.

## Why This Architecture?

### OpenTelemetry Collector

- **Single point of ingestion** — Applications send telemetry to one place. The collector handles batching, retries, backpressure, and fan-out to multiple backends.
- **Processing pipeline** — Enables sampling, attribute enrichment, and filtering without changing application code.
- **Vendor agnostic** — Export to Tempo today, swap to Datadog tomorrow by changing one config line.

### Prometheus vs. OTel Metrics

| Approach | Pros | Cons |
|----------|------|------|
| Prometheus (pull) | Mature, efficient, built-in alerting | Requires scraping configuration per target |
| OTel Metrics (push) | Unified with trace pipeline, no scrape config | Less mature, no built-in alerting |

**Our choice:** Use OTel SDK to generate metrics, push them through the Collector, and export to Prometheus. This keeps instrumentation consistent and lets Prometheus handle alerting.

### Grafana Tempo (Traces)

Tempo was chosen over Jaeger because:
- **Object storage backend** — Tempo uses object storage (S3, GCS, or local filesystem) which is cheaper and more scalable than Jaeger's Cassandra/Elasticsearch dependency.
- **Native OTLP support** — Direct OTLP ingestion without needing an agent.
- **Grafana integration** — Seamless trace-to-log and trace-to-metric correlation.

### Loki (Logs)

Loki was chosen over Elasticsearch because:
- **No indexing** — Loki indexes metadata (labels) rather than full-text content. This drastically reduces storage costs.
- **Prometheus-like** — Uses the same label-based query model, making it natural for teams already familiar with PromQL.
- **Low operational overhead** — Single binary, no JVM, no cluster management for moderate scale.

## Telemetry Flow Diagram

```
                    ┌──────────────────────┐
                    │   Application Code    │
                    │  (Python/Flask/Celery)│
                    └──────────┬───────────┘
                               │ OTLP (gRPC)
                               ▼
                    ┌──────────────────────┐
                    │  OTel Collector      │
                    │  - batch             │
                    │  - enrich attributes │
                    │  - sample traces     │
                    │  - generate span     │
                    │    metrics           │
                    └──┬───────┬───────┬───┘
                       │       │       │
              ┌────────┘       │       └────────┐
              ▼                ▼                  ▼
      ┌─────────────┐  ┌───────────┐  ┌──────────────────┐
      │  Prometheus  │  │   Tempo   │  │      Loki        │
      │  Metrics     │  │   Traces  │  │    Logs          │
      │  Port: 9090  │  │ Port: 3200│  │  Port: 3100      │
      └─────────────┘  └───────────┘  └──────────────────┘
              │                │                  │
              └────────────────┼──────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Grafana         │
                    │  Port: 3000          │
                    │  Unified UI          │
                    │  - Dashboards        │
                    │  - Explore (traces)  │
                    │  - Log queries       │
                    │  - Alerting          │
                    └──────────────────────┘
```

## Sampling Strategy

| Trace Type | Sampling Rate | Rationale |
|-----------|--------------|-----------|
| Healthy (2xx) | 10% | Low signal value for healthy requests |
| Warning (4xx) | 50% | Useful to track client errors |
| Error (5xx) | 100% | Capture all failures for debugging |
| Checkout/Payment | 100% | Business-critical path |

The Collector's `probabilistic_sampler` processor handles rate-based sampling, while the head-based sampler in the SDK ensures critical spans are never dropped.

## Storage & Retention

| Data Source | Retention | Storage Backend | Size Estimate |
|------------|-----------|----------------|---------------|
| Prometheus Metrics | 30 days | Local TSDB | ~50 GB |
| Tempo Traces | 14 days | Local FS → S3 | ~100 GB |
| Loki Logs | 30 days | Local FS → S3 | ~200 GB |

For production, all storage backends should point to S3-compatible object storage for durability and cost efficiency.

## Scaling Considerations

| Bottleneck | Mitigation |
|-----------|------------|
| Trace ingestion spike | Collector batching + queue + backpressure |
| High cardinality metrics | Recording rules pre-aggregate; drop high-cardinality labels |
| Log volume | Loki's `tsdb` store + retention policies |
| Dashboard query load | Prometheus recording rules + Grafana caching |
| Single Collector failure | Run multiple Collectors behind a load balancer (gRPC) |
