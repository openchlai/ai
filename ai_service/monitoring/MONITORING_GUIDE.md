# AI Service Monitoring Guide

Complete guide for monitoring the AI service using Prometheus and Grafana.

---

## 📋 Prerequisites

Before you start, ensure you have:
- **Docker & Docker Compose** installed (recommended) OR
- **Python 3.9+** with pip installed (for local development)
- The AI service running (either via Docker or locally)
- Access to `localhost` on your machine

**Quick Check**:
```bash
# For Docker setup
docker compose ps

# For local setup
curl http://localhost:8125/health
```

---

## 🚀 Quick Access

### Grafana (Dashboards & Visualization)
- **URL**: http://localhost:3000
- **Username**: `admin`
- **Password**: `admin` (change on first login)
- **What it does**: Beautiful real-time dashboards showing system performance

### Prometheus (Metrics & Queries)
- **URL**: http://localhost:9090
- **What it does**: Time-series metrics database and query engine

### API Metrics Endpoint
- **URL**: http://localhost:8125/metrics
- **What it does**: Raw Prometheus metrics from the FastAPI application

---

## 📖 What You'll Learn

This guide covers:
- **Getting Started**: How to access and navigate Grafana and Prometheus
- **Common Use Cases**: Health checks, debugging, load testing, capacity planning
- **Setup Instructions**: Both Docker (recommended) and local development
- **Metrics Reference**: Understanding all tracked metrics with example queries
- **Troubleshooting**: Solutions to common problems
- **Advanced Topics**: Custom dashboards, alerts, and data export

**New to monitoring?** Start with "Getting Started with Grafana" below, then explore "Common Use Cases" to see practical examples.

---

## 📊 Getting Started with Grafana

### 1. First Login

1. Open http://localhost:3000 in your browser
2. Login with `admin` / `admin`
3. You'll be prompted to change the password (recommended for production)

**Troubleshooting**: If you can't access Grafana:
- Check if Docker container is running: `docker compose ps grafana`
- Check if port 3000 is available: `sudo lsof -i :3000`
- View Grafana logs: `docker compose logs grafana`

### 2. Navigate to Dashboards

**Option A: Via Menu**
1. Click the **☰** (hamburger menu) in the top-left corner
2. Select **Dashboards**
3. You'll see available dashboards listed

**Option B: Direct Links**
- System Overview: http://localhost:3000/d/system-overview
- API Performance: http://localhost:3000/d/api-performance

### 3. Understanding the Dashboard

**Time Range Selector** (top-right):
- Click to change time window (Last 5m, Last 1h, Last 24h, etc.)
- Default: Last 15 minutes with auto-refresh every 10 seconds

**Refresh Button**:
- Click the circular arrow icon to refresh data immediately
- Set auto-refresh interval from the dropdown

**Panel Navigation**:
- Each box is a "panel" showing a specific metric
- Hover over a panel to see more details
- Click panel title → View to see full-screen version

### 4. Key Metrics to Watch

**System Overview Dashboard**:
- **Requests Per Second**: How many API calls are being processed
- **Average Response Time**: How long requests take (lower is better)
- **Error Rate**: Percentage of failed requests (should be < 1%)
- **Queue Length**: Number of pending tasks (should be < 10)
- **CPU Usage**: Overall CPU utilization (warning if > 90%)
- **Memory Usage**: Available memory (warning if < 10%)

**API Performance Dashboard**:
- **Requests by Endpoint**: Which API endpoints are most used
- **Response Time Distribution**: p50, p95, p99 latencies
- **Error Rates by Endpoint**: Which endpoints are failing
- **Concurrent Requests**: How many active requests right now

---

## 🔍 Using Prometheus

### 1. Access Prometheus

Open http://localhost:9090 in your browser

### 2. Run Queries

**Try these example queries in the query box**:

```promql
# Total API requests per second
sum(rate(http_requests_total[1m]))

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Queue length
celery_queue_length

# CPU usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

Click **Execute** to run the query and see results.

### 3. View Targets

Check if all services are being monitored:

1. Go to http://localhost:9090/targets
2. All targets should show **UP** status:
   - `ai-pipeline` - FastAPI application metrics
   - `celery` - Task queue metrics
   - `node-exporter` - System metrics (CPU, memory, disk)
   - `redis` - Redis database metrics
   - `prometheus` - Prometheus itself

If any target is **DOWN**, check the service logs.

### 4. View Alerts

See active alerts: http://localhost:9090/alerts

**Configured Alerts**:
- High Error Rate (> 5% for 2 minutes)
- High Response Time (p95 > 30s for 5 minutes)
- Queue Backup (> 50 tasks for 5 minutes)
- Low Memory (< 10% available)

---

## 🎯 Common Use Cases

### Use Case 1: Check System Health

**Quick Health Check**:
1. Open Grafana: http://localhost:3000
2. Go to System Overview dashboard
3. Look at the top row:
   - ✅ Green = Healthy
   - ⚠️ Yellow = Warning
   - ❌ Red = Critical

**What to look for**:
- Requests per second: Steady is good, sudden drops are bad
- Error rate: < 1% is good
- Response time: < 5 seconds is good
- Queue length: < 10 is good

### Use Case 2: Investigate Slow Responses

**Step 1**: Go to API Performance dashboard

**Step 2**: Check "Response Time by Endpoint" panel
- Identifies which endpoints are slowest

**Step 3**: Click on the slow endpoint panel
- See time-series graph of when it became slow

**Step 4**: Check the response time metrics
- Look at model processing time metrics to see which AI model is slowest
- Note: Model-level metrics are tracked in the application but may not appear in separate dashboard panels

### Use Case 3: Debug Failed Requests

**Step 1**: Go to API Performance dashboard

**Step 2**: Check "Error Rate by Endpoint" panel
- Identifies which endpoints are failing

**Step 3**: Note the time when errors spiked

**Step 4**: Check application logs for that timeframe
```bash
docker compose logs ai-pipeline --since 5m
```

### Use Case 4: Load Testing Analysis

**Before load test**:
1. Open System Overview dashboard
2. Note baseline metrics (requests/sec, response time)

**During load test**:
1. Watch dashboard update in real-time
2. Observe which resource hits limits first:
   - CPU maxes out → CPU bottleneck
   - Queue length grows → Worker capacity bottleneck
   - Response time spikes → Model performance bottleneck

**After load test**:
1. Take screenshots of dashboard
2. Export metrics for reporting
3. Document findings

### Use Case 5: Capacity Planning

**Monthly Review**:
1. Set time range to "Last 30 days"
2. Check peak usage metrics:
   - Peak requests per second
   - Peak queue length
   - Peak CPU/memory usage
3. Plan infrastructure scaling before hitting limits

---

## 🛠️ Setup Instructions

### For Docker (Recommended)

**Start monitoring stack**:
```bash
# Start all services including monitoring
docker compose up -d

# Verify services are running
docker compose ps

# Check if Grafana is accessible
curl http://localhost:3000/api/health
```

**Access dashboards**:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- Metrics: http://localhost:8125/metrics

**What happens next**:
1. Grafana starts and auto-loads the pre-configured dashboards
2. Prometheus starts scraping metrics from all exporters every 15 seconds
3. Within 1-2 minutes, you'll see live data in Grafana dashboards
4. If dashboards are empty, wait a bit longer or send some test requests to the API

### For Local Development (Without Docker)

**Note**: When running locally without Docker, you can view metrics at the `/metrics` endpoint, but you won't have Grafana dashboards unless you install Prometheus and Grafana separately (see instructions below).

**Install dependencies**:
```bash
pip install prometheus-client==0.22.1
pip install prometheus-fastapi-instrumentator==7.0.0
```

**Start services**:
```bash
# Terminal 1: FastAPI
python -m app.main

# Terminal 2: Celery Worker
celery -A app.celery_app worker --loglevel=info -E --pool=solo -Q model_processing,celery

# Terminal 3: Redis (if not running)
redis-server
```

**View metrics**:
```bash
# View all metrics
curl http://localhost:8125/metrics

# View specific metrics
curl http://localhost:8125/metrics | grep http_requests_total

# Watch metrics update (refreshes every 2 seconds)
watch -n 2 'curl -s http://localhost:8125/metrics | head -50'
```

**Optional: Install Prometheus/Grafana locally**:

**Linux**:
```bash
# Download and install Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz
cd prometheus-2.48.0.linux-amd64

# Run Prometheus (replace /path/to/ with actual path to your project)
./prometheus --config.file=/home/marlon/ai/ai_service/monitoring/prometheus.yml

# In a new terminal, download and install Grafana
cd /tmp
wget https://dl.grafana.com/oss/release/grafana-10.2.2.linux-amd64.tar.gz
tar -zxvf grafana-10.2.2.linux-amd64.tar.gz
cd grafana-10.2.2

# Run Grafana
./bin/grafana-server
```

**macOS**:
```bash
# Install with Homebrew
brew install prometheus grafana

# Start services
brew services start prometheus
brew services start grafana
```

---

## 📈 Key Metrics Explained

### API Metrics

**Total Requests**:
```promql
http_requests_total
```
- Counter that increases with each request
- Labels: `method`, `endpoint`, `status`

**Request Rate** (requests per second):
```promql
rate(http_requests_total[1m])
```
- Good: Steady rate matching expected traffic
- Bad: Sudden drops (service down) or spikes (attack/bug)

**Response Time** (p95 - 95th percentile):
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```
- 95% of requests complete within this time
- Good: < 5 seconds
- Warning: 5-10 seconds
- Critical: > 10 seconds

**Error Rate** (percentage):
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```
- Good: < 1%
- Warning: 1-5%
- Critical: > 5%

### Model Processing Metrics

**Processing Time by Model**:
```promql
rate(model_processing_seconds_sum{model="whisper"}[5m]) / rate(model_processing_seconds_count{model="whisper"}[5m])
```
- Average time each model takes
- Typical values:
  - Whisper: 2-5 seconds per minute of audio
  - NER: 0.5-2 seconds
  - Classifier: 0.3-1 second
  - Translator: 1-3 seconds

**Model Success Rate**:
```promql
sum(rate(model_operations_total{status="success"}[5m])) / sum(rate(model_operations_total[5m])) * 100
```
- Percentage of successful model operations
- Good: > 95%

### Celery Metrics

**Queue Length**:
```promql
celery_queue_length
```
- Number of pending tasks
- Good: < 10
- Warning: 10-50
- Critical: > 50 (worker bottleneck)

**Task Throughput** (tasks per minute):
```promql
sum(rate(celery_tasks_total{state="SUCCESS"}[5m])) * 60
```
- How many tasks are being completed
- Compare with request rate to check if workers are keeping up

**Task Duration**:
```promql
rate(celery_task_duration_seconds_sum[5m]) / rate(celery_task_duration_seconds_count[5m])
```
- Average time to complete a task
- Includes queuing time + processing time

### System Metrics

**CPU Usage** (percentage):
```promql
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
- Good: < 70%
- Warning: 70-90%
- Critical: > 90% (CPU bottleneck)

**Memory Available** (percentage):
```promql
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100
```
- Good: > 20%
- Warning: 10-20%
- Critical: < 10% (memory bottleneck)

**Disk Usage** (percentage):
```promql
100 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100)
```
- Warning: > 80%
- Critical: > 90%

---

## 🔧 Troubleshooting

### Problem: Grafana Dashboard is Empty

**Possible Causes**:
1. Prometheus not scraping metrics
2. Wrong data source configured
3. Incorrect metric names in dashboard

**Solution**:
```bash
# Check Prometheus targets
open http://localhost:9090/targets

# All should show UP. If DOWN:
docker compose logs prometheus
docker compose restart prometheus

# Check data source in Grafana
# Go to Configuration → Data Sources → Prometheus
# URL should be: http://prometheus:9090
# Click "Save & Test" - should show green checkmark
```

### Problem: Some Metrics Missing

**Check which metrics are available**:
```bash
curl http://localhost:8125/metrics
```

**If no metrics at all**:
```bash
# Check if ENABLE_METRICS is true in .env
grep ENABLE_METRICS .env

# Restart FastAPI
docker compose restart ai-pipeline
```

**If only some metrics missing**:
- Check that Celery worker is running
- Verify Redis connection
- Check application logs for errors

### Problem: Prometheus Target is DOWN

**Check target status**:
```bash
open http://localhost:9090/targets
```

**If `ai-pipeline` is DOWN**:
```bash
# Check if container is running
docker compose ps ai-pipeline

# Check if metrics endpoint works
curl http://localhost:8125/metrics

# Check Prometheus can reach it
docker compose exec prometheus wget -O- http://ai-pipeline:8125/metrics

# Restart Prometheus to reload config
docker compose restart prometheus
```

### Problem: High Memory Usage in Grafana

**Grafana using too much memory**:
```bash
# Check resource usage
docker stats grafana

# If high, restart Grafana
docker compose restart grafana
```

### Problem: Can't Login to Grafana

**If default credentials don't work**:
```bash
# Reset Grafana admin password
docker compose exec grafana grafana-cli admin reset-admin-password newpassword

# Or check environment variables
docker compose exec grafana env | grep GF_
```

### Problem: Dashboards Not Auto-Loading

**Check dashboard provisioning**:
```bash
# Verify dashboard files are in container
docker compose exec grafana ls -la /etc/grafana/provisioning/dashboards/

# Check Grafana logs
docker compose logs grafana | grep -i dashboard

# Restart Grafana to reload dashboards
docker compose restart grafana
```

---

## 🎓 Advanced Usage

### Creating Custom Dashboards

**Step 1**: Click **+** (plus icon) → **Dashboard**

**Step 2**: Click **Add visualization**

**Step 3**: Select **Prometheus** as data source

**Step 4**: Enter a PromQL query, for example:
```promql
rate(http_requests_total[5m])
```

**Step 5**: Configure visualization:
- Choose chart type (Graph, Gauge, Table, etc.)
- Set title, colors, thresholds
- Add legends and tooltips

**Step 6**: Click **Apply** to save panel

**Step 7**: Add more panels, then click **Save** dashboard

### Exporting Metrics for Reports

**Export from Prometheus**:
```bash
# Query API for time-series data
curl -G 'http://localhost:9090/api/v1/query_range' \
  --data-urlencode 'query=http_requests_total' \
  --data-urlencode 'start=2024-01-01T00:00:00Z' \
  --data-urlencode 'end=2024-01-01T23:59:59Z' \
  --data-urlencode 'step=60s' > metrics.json
```

**Export from Grafana**:
1. Open dashboard
2. Click **Share** (top-right)
3. Go to **Export** tab
4. Click **Save to file**
5. Saves dashboard JSON configuration

**Take Screenshots**:
1. Open dashboard
2. Click **Share** → **Snapshot**
3. Or use browser screenshot tool

### Setting Up Alerts in Grafana

**Step 1**: Create or edit a dashboard panel

**Step 2**: Click panel title → **Edit**

**Step 3**: Go to **Alert** tab

**Step 4**: Click **Create Alert**

**Step 5**: Configure alert rule:
- Set condition (e.g., "WHEN avg() IS ABOVE 90")
- Set evaluation frequency (e.g., "Every 1m for 5m")
- Add description explaining what the alert means

**Step 6**: Add notification channel:
- Go to **Alerting** → **Notification channels**
- Add Slack, Email, PagerDuty, etc.

**Step 7**: Save panel and dashboard

### Load Testing Workflow

**Step 1: Start monitoring**
```bash
# Ensure all services are up
docker compose up -d

# Open Grafana dashboard
open http://localhost:3000
```

**Step 2: Note baseline metrics**
- Current requests/sec: ___
- Current response time: ___
- Current queue length: ___

**Step 3: Run load test**
```bash
# Install locust if needed
pip install locust

# Run load test
locust -f locustfile.py --headless -u 100 -r 10 -t 10m --host=http://localhost:8125
```

**Step 4: Monitor in real-time**
- Watch System Overview dashboard
- Note when metrics degrade
- Identify which resource maxes out first

**Step 5: Capture results**
- Take dashboard screenshots
- Export metrics data
- Document bottlenecks found

**Step 6: Analyze findings**
- Which component is the bottleneck?
- At what load does it fail?
- What's the recommended fix?

---

## 📊 Monitoring Architecture

```
┌─────────────────────────────────────────────┐
│          Grafana (Port 3000)                │
│       Visualization & Dashboards            │
└────────────────┬────────────────────────────┘
                 │ Queries metrics
                 ▼
┌─────────────────────────────────────────────┐
│        Prometheus (Port 9090)               │
│     Time-Series Metrics Database            │
└────────────────┬────────────────────────────┘
                 │ Scrapes every 15s
                 ▼
┌─────────────────────────────────────────────┐
│           Metrics Exporters                 │
│                                             │
│  • FastAPI (:8125/metrics)                  │
│    - HTTP requests, response times          │
│    - Model processing times                 │
│    - Custom application metrics             │
│                                             │
│  • Node Exporter (:9100)                    │
│    - CPU, Memory, Disk, Network             │
│    - System-level metrics                   │
│                                             │
│  • Redis Exporter (:9121)                   │
│    - Redis database metrics                 │
│    - Memory usage, commands/sec             │
│                                             │
│  • Celery Exporter (:9808)                  │
│    - Task queue metrics                     │
│    - Active workers, task counts            │
└─────────────────────────────────────────────┘
```

**How it works**:
1. Application exposes metrics at `/metrics` endpoint
2. Prometheus scrapes all exporters every 15 seconds
3. Prometheus stores metrics in time-series database
4. Grafana queries Prometheus and displays dashboards
5. You view real-time dashboards in web browser

---

## 📝 Quick Commands Reference

```bash
# Start monitoring stack (Docker)
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f grafana
docker compose logs -f prometheus

# Restart services
docker compose restart grafana
docker compose restart prometheus

# Stop monitoring
docker compose down

# View metrics endpoint
curl http://localhost:8125/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health

# Run load test
locust -f locustfile.py --headless -u 50 -r 5 -t 5m --host=http://localhost:8125

# Watch metrics update (local dev)
watch -n 2 'curl -s http://localhost:8125/metrics | grep http_requests_total'

# Export metrics to file
curl -s http://localhost:8125/metrics > metrics_$(date +%Y%m%d_%H%M%S).txt
```

---

## 🎯 Best Practices

### For Daily Monitoring
1. Check System Overview dashboard once per day
2. Look for unusual spikes or drops
3. Verify error rate stays < 1%
4. Ensure queue length stays < 10

### For Incidents
1. Note the time incident started
2. Check API Performance dashboard for affected endpoints
3. Check System Metrics for resource constraints
4. Export metrics and logs for analysis
5. Document root cause and fix

### For Load Testing
1. Start with low load (10 users) to verify baseline
2. Gradually increase load to find breaking point
3. Monitor all metrics during test
4. Take screenshots at key load levels
5. Document maximum sustainable load

### For Production
1. Set up Grafana alerts for critical metrics
2. Configure notification channels (Slack, email)
3. Change default Grafana password
4. Enable HTTPS with reverse proxy
5. Regular backup of Grafana dashboards
6. Monitor disk usage of Prometheus data

---

## 🆘 Getting Help

**Service not responding?**
```bash
# Check if services are running
docker compose ps

# Check logs for errors
docker compose logs --tail=100 grafana
docker compose logs --tail=100 prometheus

# Restart everything
docker compose restart
```

**Still having issues?**
1. Check service logs for error messages
2. Verify network connectivity between containers
3. Ensure ports are not already in use
4. Check `.env` file for correct configuration
5. Try stopping and restarting Docker Compose

**Useful URLs**:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Prometheus Targets: http://localhost:9090/targets
- Prometheus Alerts: http://localhost:9090/alerts
- API Metrics: http://localhost:8125/metrics
- API Health: http://localhost:8125/health

---

**You're ready to monitor your AI service!** 🚀

For questions or issues, check the application logs first:
```bash
docker compose logs -f
```
