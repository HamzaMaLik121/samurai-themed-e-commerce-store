# Observability Stack

> A production-grade observability architecture for the Samurai E-Commerce platform, combining **OpenTelemetry**, **Prometheus**, **Grafana Tempo**, **Loki**, and **Grafana** into a unified telemetry pipeline.

## Architecture Overview

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Application Layer                      │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
                    │  │ Frontend │  │ Backend  │  │  Worker  │  │  Auth    │ │
                    │  │  (React) │  │ (Flask)  │  │ (Celery) │  │ Service  │ │
                    │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
                    │       │              │              │              │      │
                    │       └──────────────┴──────────────┴──────────────┘      │
                    │                        │ OpenTelemetry SDK                  │
                    └────────────────────────┼──────────────────────────────────┘
                                             │ OTLP (gRPC)
                    ┌────────────────────────┼──────────────────────────────────┐
                    │              OpenTelemetry Collector                       │
                    │  ┌──────────────┐  ┌──┴───┐  ┌───────────┐               │
                    │  │  OTLP Recv   │  │Batch │  │  Health   │               │
                    │  │  (4317/4318) │  │Proc  │  │  Check    │               │
                    │  └──────┬───────┘  └──┬───┘  └───────────┘               │
                    │         │              │                                  │
                    │  ┌──────┴──────────────┴──────────────────────────────┐  │
                    │  │                   Exporters                        │  │
                    │  │  ┌─────────┐  ┌──────────┐  ┌────────────────┐    │  │
                    │  │  │Prometheus│  │  Tempo   │  │     Loki      │    │  │
                    │  │  │  (push) │  │ (traces) │  │    (logs)     │    │  │
                    │  │  └────┬────┘  └────┬─────┘  └──────┬─────────┘    │  │
                    │  └───────┼────────────┼───────────────┼──────────────┘  │
                    └──────────┼────────────┼───────────────┼─────────────────┘
                               │            │               │
          ┌────────────────────┼────────────┼───────────────┼─────────────────┐
          │        Storage & Query Layer                                       │
          │  ┌──────────┴─┐  ┌──┴────────┐  ┌──┴──────────┐                 │
          │  │ Prometheus │  │   Tempo   │  │    Loki     │                 │
          │  │ (Metrics)  │  │ (Traces)  │  │   (Logs)    │                 │
          │  └────────────┘  └───────────┘  └─────────────┘                 │
          └────────────────────────┬─────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────────────────────┐
          │                 Visualization Layer                               │
          │  ┌─────────────────────┴──────────────────────────────────────┐  │
          │  │                     Grafana                                 │  │
          │  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │  │
          │  │  │  Overview  │  │   Traces   │  │  Business Metrics  │    │  │
          │  │  │ Dashboard  │  │  Dashboard │  │    Dashboard       │    │  │
          │  │  └────────────┘  └────────────┘  └────────────────────┘    │  │
          │  └───────────────────────────────────────────────────────────┘  │
          └─────────────────────────────────────────────────────────────────┘
```

## Stack Components

| Component | Purpose | Port |
|-----------|---------|------|
| **OpenTelemetry Collector** | Receives, processes, and exports telemetry data | `4317` (gRPC), `4318` (HTTP) |
| **Prometheus** | Time-series metrics storage and alerting | `9090` |
| **Grafana Tempo** | Distributed tracing backend | `3200` (query), `4317` (OTLP) |
| **Loki** | Log aggregation system | `3100` |
| **Grafana** | Unified visualization and dashboards | `3000` |
| **Alertmanager** | Alert routing and notification management | `9093` |

## Quick Start

```bash
# Start the entire observability stack
docker-compose -f Observability/docker-compose.yml up -d

# Access Grafana
open http://localhost:3000  # admin / admin

# Verify collector health
curl http://localhost:13133
```

## Directory Structure

```
Observability/
├── README.md                    # This file
├── docker-compose.yml           # Complete observability stack
├── otel-collector/              # OpenTelemetry Collector configuration
│   ├── config.yaml              # Collector pipeline & exporters
│   └── collector-metrics.yaml   # Alternative config with enhanced metrics
├── prometheus/                  # Metrics configuration
│   ├── prometheus.yml           # Scrape configuration
│   └── rules/                   # Alerting & recording rules
├── tempo/                       # Distributed tracing
│   └── tempo.yaml               # Tempo backend configuration
├── loki/                        # Log aggregation
│   └── loki.yaml                # Loki configuration
├── grafana/                     # Visualization
│   ├── dashboards/              # Pre-built dashboard JSON models
│   └── provisioning/            # Auto-provisioning configuration
├── instrumentation/             # Application instrumentation guides
│   ├── python/                  # Python SDK setup & examples
│   └── flask/                   # Flask-specific middleware
└── docs/                        # Detailed documentation
    ├── architecture.md          # Deep dive into architecture decisions
    ├── setup.md                 # Step-by-step setup guide
    └── dashboards.md            # Dashboard usage and interpretation
```

## Core Flows

### 1. Distributed Tracing Flow
```
Request → Flask App → OTel SDK → OTLP → Collector → Tempo → Grafana Explore
```

### 2. Metrics Pipeline
```
App Metrics → OTel SDK → Prometheus Export → Collector → Prometheus → Grafana Dashboards
```

### 3. Log Aggregation
```
App Logs → Loki Promtail (or OTel) → Loki → Grafana Log Explorer
```

### 4. Alert Flow
```
Prometheus Rules → Alertmanager → Slack/Email/PagerDuty
```
