#!/bin/bash

# Local Development Monitoring Setup
# For running AI service without Docker

set -e

echo "🎯 AI Service - Local Development Monitoring"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Python virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
    echo "It's recommended to use a virtual environment"
    echo ""
fi

# Check if required packages are installed
echo "📦 Checking Python dependencies..."
if python -c "import prometheus_client" 2>/dev/null; then
    echo -e "${GREEN}✅ prometheus-client installed${NC}"
else
    echo -e "${RED}❌ prometheus-client not installed${NC}"
    echo "Installing prometheus-client..."
    pip install prometheus-client==0.21.1
fi

if python -c "import prometheus_fastapi_instrumentator" 2>/dev/null; then
    echo -e "${GREEN}✅ prometheus-fastapi-instrumentator installed${NC}"
else
    echo -e "${RED}❌ prometheus-fastapi-instrumentator not installed${NC}"
    echo "Installing prometheus-fastapi-instrumentator..."
    pip install prometheus-fastapi-instrumentator==7.0.0
fi

echo ""
echo "============================================="
echo -e "${GREEN}✅ Monitoring dependencies ready!${NC}"
echo "============================================="
echo ""

echo "📊 Monitoring Options for Local Development:"
echo ""
echo "Option 1: Lightweight Metrics Export (Recommended)"
echo "  - Your FastAPI app exposes /metrics endpoint"
echo "  - View metrics: curl http://localhost:8125/metrics"
echo "  - No additional services needed"
echo ""
echo "Option 2: Standalone Prometheus + Grafana"
echo "  - Download Prometheus: https://prometheus.io/download/"
echo "  - Download Grafana: https://grafana.com/grafana/download"
echo "  - Run as standalone processes"
echo ""
echo "Option 3: Simple Monitoring Script"
echo "  - Run: python scripts/monitor_resources.py"
echo "  - Real-time console output"
echo "  - Logs to file"
echo ""
echo "============================================="
echo ""
echo "🚀 To start your AI service with monitoring:"
echo ""
echo "Terminal 1 - Start FastAPI:"
echo "  python -m app.main"
echo ""
echo "Terminal 2 - Start Celery Worker:"
echo "  celery -A app.celery_app worker --loglevel=info -E --pool=solo"
echo ""
echo "Terminal 3 - View Metrics:"
echo "  curl http://localhost:8125/metrics"
echo ""
echo "Terminal 4 - Monitor Resources (optional):"
echo "  python scripts/monitor_resources.py"
echo ""
echo "============================================="
echo ""
echo "📈 Metrics Endpoint:"
echo "  http://localhost:8125/metrics"
echo ""
echo "📖 Documentation:"
echo "  monitoring/LOCAL_SETUP.md"
echo ""
