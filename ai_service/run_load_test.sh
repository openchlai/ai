#!/bin/bash
#
# AI Service Load Testing Runner
# ===============================
#
# Unified script to run load tests with different configurations.
# Automatically creates timestamped result directories and generates reports.
#
# Usage:
#   ./run_load_test.sh quick      # 5 min,  10 users  (quick smoke test)
#   ./run_load_test.sh standard   # 15 min, 20 users  (standard load test)
#   ./run_load_test.sh extended   # 30 min, 50 users  (extended load test)
#   ./run_load_test.sh stress     # 1 hour, 100 users (stress test)
#   ./run_load_test.sh custom <users> <duration> <spawn-rate>

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOST="${LOAD_TEST_HOST:-http://localhost:8125}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="test_reports/load_test_results_${TIMESTAMP}"

# Print banner
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        AI Service Load Testing Framework                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print section headers
print_header() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if locust is installed
if ! command -v locust &> /dev/null; then
    print_error "Locust is not installed"
    echo "Install with: pip install locust"
    exit 1
fi

# Check if load_test.py exists
if [ ! -f "load_test.py" ]; then
    print_error "load_test.py not found in current directory"
    exit 1
fi

# Check if test_audio directory exists
if [ ! -d "test_audio" ]; then
    print_warning "test_audio/ directory not found"
    print_warning "Audio processing tests will be skipped"
    print_warning "Create test_audio/ directory and add .wav files to test audio endpoints"
fi

# Determine test configuration
TEST_TYPE="${1:-standard}"

case "$TEST_TYPE" in
    quick)
        USERS=10
        DURATION="5m"
        SPAWN_RATE=2
        DESCRIPTION="Quick Smoke Test"
        ;;
    standard)
        USERS=20
        DURATION="15m"
        SPAWN_RATE=2
        DESCRIPTION="Standard Load Test"
        ;;
    extended)
        USERS=50
        DURATION="30m"
        SPAWN_RATE=5
        DESCRIPTION="Extended Load Test"
        ;;
    stress)
        USERS=100
        DURATION="1h"
        SPAWN_RATE=10
        DESCRIPTION="Stress Test"
        ;;
    custom)
        USERS="${2:-20}"
        DURATION="${3:-15m}"
        SPAWN_RATE="${4:-2}"
        DESCRIPTION="Custom Test Configuration"
        ;;
    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo ""
        echo "Available test types:"
        echo "  quick      - 5 min,  10 users  (quick smoke test)"
        echo "  standard   - 15 min, 20 users  (standard load test)"
        echo "  extended   - 30 min, 50 users  (extended load test)"
        echo "  stress     - 1 hour, 100 users (stress test)"
        echo "  custom <users> <duration> <spawn-rate>"
        echo ""
        echo "Examples:"
        echo "  ./run_load_test.sh quick"
        echo "  ./run_load_test.sh standard"
        echo "  ./run_load_test.sh custom 50 20m 5"
        exit 1
        ;;
esac

# Print test configuration
print_header "Test Configuration"
echo "  Type:        $DESCRIPTION"
echo "  Users:       $USERS"
echo "  Duration:    $DURATION"
echo "  Spawn Rate:  $SPAWN_RATE users/sec"
echo "  Host:        $HOST"
echo "  Results Dir: $RESULTS_DIR"
echo ""

# Create results directory
mkdir -p "$RESULTS_DIR"
print_success "Created results directory: $RESULTS_DIR"

# Check if API is reachable
print_header "Pre-flight Checks"
echo -n "  Checking API connectivity... "
if curl -s --max-time 5 "$HOST/health" > /dev/null 2>&1; then
    print_success "API is reachable"
else
    print_error "Cannot reach API at $HOST/health"
    print_error "Make sure the AI service is running:"
    echo "    docker-compose up -d"
    exit 1
fi

# Check monitoring services
echo -n "  Checking Prometheus... "
if curl -s --max-time 5 "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
    print_success "Prometheus is running"
else
    print_warning "Prometheus not reachable (monitoring disabled)"
fi

echo -n "  Checking Grafana... "
if curl -s --max-time 5 "http://localhost:3000/api/health" > /dev/null 2>&1; then
    print_success "Grafana is running (view dashboards at http://localhost:3000)"
else
    print_warning "Grafana not reachable (dashboards unavailable)"
fi

# Run the load test
print_header "Starting Load Test"
echo "  Press Ctrl+C to stop the test early"
echo ""

START_TIME=$(date +%s)

locust -f load_test.py \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="$DURATION" \
    --headless \
    --csv="${RESULTS_DIR}/stats" \
    --logfile="${RESULTS_DIR}/locust.log" \
    --loglevel=INFO

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

# Generate HTML report from CSV results
print_header "Generating HTML Report"
python generate_html_report.py "$RESULTS_DIR" || print_warning "HTML report generation failed (but CSV results available)"

# Generate summary
print_header "Test Complete"
print_success "Elapsed time: ${ELAPSED}s"
print_success "Results saved to: $RESULTS_DIR/"
echo ""

# List generated files
print_header "Generated Files"
ls -lh "$RESULTS_DIR/" | tail -n +2 | awk '{printf "  %-30s %8s\n", $9, $5}'
echo ""

# Print quick summary from CSV
if [ -f "${RESULTS_DIR}/stats_stats.csv" ]; then
    print_header "Quick Summary"

    # Extract aggregate stats (last line of CSV)
    STATS=$(tail -n 1 "${RESULTS_DIR}/stats_stats.csv")

    TOTAL_REQUESTS=$(echo "$STATS" | cut -d',' -f3)
    FAILED_REQUESTS=$(echo "$STATS" | cut -d',' -f4)
    AVG_RESPONSE=$(echo "$STATS" | cut -d',' -f6)
    P50_RESPONSE=$(echo "$STATS" | cut -d',' -f11)
    P95_RESPONSE=$(echo "$STATS" | cut -d',' -f16)
    P99_RESPONSE=$(echo "$STATS" | cut -d',' -f18)
    RPS=$(echo "$STATS" | cut -d',' -f20)

    ERROR_RATE=$(echo "scale=2; ($FAILED_REQUESTS / $TOTAL_REQUESTS) * 100" | bc)

    echo "  Total Requests:    $TOTAL_REQUESTS"
    echo "  Failed Requests:   $FAILED_REQUESTS"
    echo "  Error Rate:        ${ERROR_RATE}%"
    echo "  Throughput:        ${RPS} req/s"
    echo "  Avg Response:      ${AVG_RESPONSE}ms"
    echo "  P50 Response:      ${P50_RESPONSE}ms"
    echo "  P95 Response:      ${P95_RESPONSE}ms"
    echo "  P99 Response:      ${P99_RESPONSE}ms"
    echo ""

    # Color-code results
    if (( $(echo "$ERROR_RATE > 5" | bc -l) )); then
        print_error "High error rate: ${ERROR_RATE}% (target: <5%)"
    elif (( $(echo "$ERROR_RATE > 1" | bc -l) )); then
        print_warning "Moderate error rate: ${ERROR_RATE}% (target: <1%)"
    else
        print_success "Low error rate: ${ERROR_RATE}%"
    fi
fi

# Print next steps
print_header "Next Steps"
echo "  1. View HTML report:     open ${RESULTS_DIR}/report.html"
echo "  2. View Grafana:         open http://localhost:3000"
echo "  3. Analyze failures:     cat ${RESULTS_DIR}/stats_failures.csv"
echo "  4. Check logs:           cat ${RESULTS_DIR}/locust.log"
echo ""

print_success "Load test completed successfully!"
