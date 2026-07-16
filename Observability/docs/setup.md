# Setup Guide

> Deploy the full observability stack on your local machine or production environment.

## Prerequisites

- Docker & Docker Compose v2.20+
- Git
- Ports available: 3000, 3100, 3200, 4317, 4318, 9090, 9093, 9100, 13133, 55679, 8888

## Quick Start (Local)

```bash
# 1. Navigate to the observability directory
cd Observability

# 2. Start all services
docker-compose up -d

# 3. Verify all services are healthy
docker-compose ps

# 4. Open Grafana
open http://localhost:3000
# Username: admin
# Password: admin

# 5. Check collector health
curl http://localhost:13133
# Expected: {"status":"Server available","upSince":"..."}
```

## Verify the Stack

### 1. Check Prometheus Targets

```bash
open http://localhost:9090/targets
```

All targets should show `UP` status.

### 2. Check Tempo Readiness

```bash
curl http://localhost:3200/ready
# Expected: "ready"
```

### 3. Send a Test Trace

```bash
# Install the OTel test utility
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc

# Run the test script
python3 -c "
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint='http://localhost:4317'))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer('test')
with tracer.start_as_current_span('test-span') as span:
    span.set_attribute('test.key', 'hello-observability')
print('Trace sent! Check Grafana -> Explore -> Tempo')
"
```

### 4. Check Log Ingestion

```bash
# Send a test log through the OTel Collector
curl -X POST http://localhost:4318/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "resourceLogs": [{
      "resource": { "attributes": [{ "key": "service.name", "value": { "stringValue": "test" } }] },
      "scopeLogs": [{
        "scope": {},
        "logRecords": [{
          "timeUnixNano": "1600000000000000000",
          "severityNumber": 9,
          "severityText": "Info",
          "body": { "stringValue": "Hello from test log!" }
        }]
      }]
    }]
  }'
```

## Instrument Your Application

### Flask Application

Add to `requirements.txt`:
```
opentelemetry-distro
opentelemetry-exporter-otlp
```

Run with auto-instrumentation:
```bash
OTEL_SERVICE_NAME=samurai-backend \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
opentelemetry-instrument flask run
```

### Docker Service

Add to your `Dockerfile`:
```dockerfile
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp && \
    opentelemetry-bootstrap -a install
ENTRYPOINT ["opentelemetry-instrument"]
CMD ["flask", "run", "--host=0.0.0.0"]
```

## Production Deployment

### Docker Swarm / Kubernetes

1. **Scale Collectors**: Run 2+ OTel Collectors behind an internal load balancer.
   - Use `--set=collector.replicaCount=2` in Helm
2. **Persistent Storage**: Replace local volumes with PVCs.
3. **Ingress**: Expose Grafana through an ingress controller with TLS.
4. **Auth**: Configure Grafana with OAuth/OIDC (GitHub, Google, or SAML).
5. **Alerting**: Configure Slack/PagerDuty webhooks in Alertmanager.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GF_SECURITY_ADMIN_USER` | `admin` | Grafana admin username |
| `GF_SECURITY_ADMIN_PASSWORD` | `admin` | Grafana admin password |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` | OTLP endpoint |
| `OTEL_SERVICE_NAME` | `unknown` | Service name for traces |
| `PROMETHEUS_RETENTION` | `30d` | Metrics retention period |
| `TEMPO_RETENTION` | `336h` | Trace retention period |
| `LOKI_RETENTION` | `720h` | Log retention period |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Grafana can't connect to data sources | Services not started | `docker-compose ps` and check all are running |
| No traces in Tempo | Collector not receiving data | Check `otel-collector:4317` from app container |
| "Connection refused" on scrape | Target not running or wrong port | Verify `docker-compose ps` and port mapping |
| High memory usage | Default limits too low | Set `memory_limiter.mib` higher in collector config |
| Missing spans | Sampling dropping them | Increase `sampling_percentage` in config |
