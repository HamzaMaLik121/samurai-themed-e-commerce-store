# Auto-Instrumentation for Python Services

> Automatically instrument Flask, Django, FastAPI, and Celery services with zero code changes using the OpenTelemetry Python SDK.

## Prerequisites

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
```

## Usage

### Flask API (Backend)

```bash
# Minimal startup
OTEL_SERVICE_NAME=samurai-backend \
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
opentelemetry-instrument flask run --host=0.0.0.0 --port=5000
```

### Celery Worker

```bash
OTEL_SERVICE_NAME=samurai-worker \
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317 \
opentelemetry-instrument celery -A tasks worker --loglevel=info
```

### Full Configuration

```bash
export OTEL_SERVICE_NAME=samurai-backend
export OTEL_SERVICE_NAMESPACE=samurai
export OTEL_SERVICE_VERSION=1.0.0
export OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_RESOURCE_ATTRIBUTES=deployment.environment=production,service.version=1.0.0
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.5
export OTEL_PYTHON_LOG_CORRELATION=true
export OTEL_PYTHON_LOG_LEVEL=info

opentelemetry-instrument flask run
```

### Docker Integration

```dockerfile
FROM python:3.12-slim

# Install OTel
RUN pip install opentelemetry-distro opentelemetry-exporter-otlp && \
    opentelemetry-bootstrap -a install

COPY . /app
WORKDIR /app

# Wrap the normal CMD with instrumentation
ENTRYPOINT ["opentelemetry-instrument"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
```

## What Gets Instrumented

| Library | Spans Generated |
|---------|----------------|
| Flask | HTTP request/response, template rendering |
| Requests/urllib3 | Outbound HTTP calls |
| SQLAlchemy | Database queries |
| Redis | Cache operations |
| Celery | Task execution |
| boto3 | AWS SDK calls (S3, DynamoDB, etc.) |
| gRPC | RPC calls |
| Kafka | Produce/consume operations |
