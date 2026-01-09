#!/bin/bash

# AI Service Monitoring Stack - Quick Start Script
# This script helps you get the monitoring stack up and running

set -e

echo "🎯 AI Service Monitoring Stack Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "📦 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"

# Check if docker-compose is available
echo "📦 Checking Docker Compose..."
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is available${NC}"

# Check if monitoring directory exists
if [ ! -d "monitoring" ]; then
    echo -e "${RED}❌ Monitoring directory not found. Are you in the project root?${NC}"
    exit 1
fi

# Pull Docker images
echo ""
echo "📥 Pulling Docker images..."
$DOCKER_COMPOSE pull prometheus grafana node-exporter redis-exporter celery-exporter

# Start monitoring stack
echo ""
echo "🚀 Starting monitoring stack..."
$DOCKER_COMPOSE up -d prometheus grafana node-exporter redis-exporter celery-exporter

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo ""
echo "🔍 Checking service status..."

check_service() {
    local service=$1
    local port=$2
    if $DOCKER_COMPOSE ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✅ $service is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service is not running${NC}"
        return 1
    fi
}

check_service "prometheus" "9090"
check_service "grafana" "3000"
check_service "node-exporter" "9100"
check_service "redis-exporter" "9121"

# Check if GPU exporter is running (optional)
if $DOCKER_COMPOSE ps | grep -q "nvidia-gpu-exporter"; then
    check_service "nvidia-gpu-exporter" "9445"
else
    echo -e "${YELLOW}⚠️  GPU exporter not running (normal if no GPU)${NC}"
fi

# Test Prometheus
echo ""
echo "🧪 Testing Prometheus..."
if curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}✅ Prometheus is healthy${NC}"
else
    echo -e "${RED}❌ Prometheus health check failed${NC}"
fi

# Test Grafana
echo ""
echo "🧪 Testing Grafana..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✅ Grafana is healthy${NC}"
else
    echo -e "${RED}❌ Grafana health check failed${NC}"
fi

# Display access information
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Monitoring Stack is Ready!${NC}"
echo "=========================================="
echo ""
echo "📊 Access Points:"
echo "  Grafana:    http://localhost:3000"
echo "              Username: admin"
echo "              Password: admin"
echo ""
echo "  Prometheus: http://localhost:9090"
echo ""
echo "  Metrics:    http://localhost:8125/metrics"
echo ""
echo "=========================================="
echo ""
echo "📚 Next Steps:"
echo "  1. Open Grafana: http://localhost:3000"
echo "  2. Login with admin/admin"
echo "  3. Navigate to Dashboards → Browse"
echo "  4. Open 'AI Service - System Overview'"
echo "  5. Start your AI service to see metrics"
echo ""
echo "📖 Documentation: monitoring/README.md"
echo ""
echo "🛑 To stop: $DOCKER_COMPOSE down"
echo "=========================================="
