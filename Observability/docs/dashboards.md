# Dashboard Guide

> How to use and interpret the pre-configured Grafana dashboards for the Samurai Shop platform.

## 1. Platform Overview Dashboard

**Location:** Grafana → Dashboards → Samurai Shop → Platform Overview  
**Refresh:** `30s`  
**Time range:** `Last 6 hours` (adjustable)

### Panels Explained

| Panel | What It Shows | Why It Matters |
|-------|---------------|----------------|
| **Service Health** | Number of healthy upstream services | If this drops below total count, a service is down |
| **Request Rate** | HTTP requests per second by status code | Spikes in 4xx/5xx indicate client errors or failures |
| **P95 Latency** | 95th percentile response time | If >2s, users are experiencing slowness |
| **Error Rate** | Percentage of 5xx responses | >5% means something is broken |
| **Active Users** | Concurrent active sessions | Drops may indicate traffic loss |
| **Orders (24h)** | Total orders in last 24 hours | Core business KPI |
| **Revenue (24h)** | Total revenue in last 24 hours | Core business KPI |
| **Top Endpoints** | Most frequently called API endpoints | Identifies hot paths and potential bottlenecks |
| **Host Resources** | CPU and Memory utilization | >80% sustained may need scaling |
| **Recent Alerts** | Currently firing alerts | Immediate action items |

### Reading the Dashboard

```
Green  → Everything is healthy
Yellow → Warning threshold approaching
Red    → Critical — needs immediate attention
```

### Drill-Down Workflow

1. Notice high **Error Rate** on Platform Overview
2. Click the error panel → "Inspect" → "Data" to see which endpoint is failing
3. Open **Explore** → select **Tempo** → search `{service.name="samurai-backend", http.status_code=~"5.."}`
4. Click a failing trace → **Logs** tab → see the exact error message

## 2. Business Metrics Dashboard

**Location:** Grafana → Dashboards → Samurai Shop → Business Metrics  
**Refresh:** `1m`  
**Time range:** `Last 24 hours`

### Key Business Panels

| Metric | Healthy Range | Action if Out of Range |
|--------|--------------|------------------------|
| **Conversion Rate** | 2–5% | <2%: Check checkout flow, payment provider |
| **Cart Abandonment** | <70% | >70%: Review cart UX, shipping costs, payment options |
| **Avg Order Value** | Stable or growing | Declining: Review pricing, upsells |
| **Checkout Funnel** | Cart > Checkout > Orders | Sharp drop at any stage indicates a friction point |

### Business Decision Workflow

```
Dashboard detects:
  └── Cart Abandonment > 75% (Red)
        ├── Check if there's a known promotion ending (expected)
        ├── Check Checkout Funnel panel for where users drop off
        ├── Cross-reference with Traces dashboard for checkout errors
        ├── If payment errors: contact payment provider
        └── If no errors: schedule UX review
```

## 3. Distributed Tracing Dashboard

**Location:** Grafana → Dashboards → Samurai Shop → Distributed Tracing  
**Refresh:** `1m`  
**Time range:** `Last 2 hours`

### Understanding Traces

A **trace** represents a single end-user request's journey through all services:

```
[Frontend] --> [Backend API] --> [Database]
                        |--> [Payment Gateway]
                        |--> [Email Service]
```

Each step is a **span** with:
- **Duration**: How long that step took
- **Status**: OK or Error
- **Attributes**: HTTP method, URL, user ID, etc.

### Finding the Root Cause

1. Look for red spans (errors) in the trace waterfall
2. Click the error span → see the exception stack trace
3. Check the `http.status_code` attribute — `500` means server error, `400` means client error
4. Check the `exception.message` for the exact error text

### Trace-to-Log Correlation

```
Trace ID: abc123def456
         │
         ▼
Loki Log: trace_id=abc123def456 level=error msg="Payment declined"
         │
         ▼
Root cause found in logs!
```

## 4. Alerting

### Alert States

| State | Meaning | Action |
|-------|---------|--------|
| **Firing** | Condition is currently true | Investigate immediately |
| **Pending** | Condition is true but not yet for duration | Watch — may auto-resolve |
| **Resolved** | Condition returned to normal | Verify fix worked |

### Acknowledging Alerts

1. **Silence**: Mute a specific alert for 1h if it's a known issue
2. **PagerDuty Acknowledge**: Critical alerts auto-assign to on-call
3. **Comment**: Add context for team members

## Tips & Best Practices

1. **Set dashboard time ranges appropriately:**
   - Operational issues: last 15–30 minutes
   - Trend analysis: last 7–30 days
   - SLO calculation: last 30 days

2. **Use annotations:**
   Add deployment annotations to correlate code changes with metric changes:
   ```
   Shift+Click on a timeline → "Add Annotation"
   Example: "Deployed v1.2.3 - fixed checkout timeout"
   ```

3. **Create alerts from panels:**
   Click a panel → "Alert" → "Create alert rule from this panel"

4. **Share dashboards:**
   Click the share icon → "Link" → copy the URL for your team
