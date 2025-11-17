#!/bin/bash
# EDRS Test Service Waiter
# Waits for all test services to be ready

set -e

echo "⏳ Waiting for EDRS Test Services..."
echo "===================================="

# Service configuration
POSTGRES_HOST="${TEST_POSTGRES_HOST:-postgres-test}"
MONGO_HOST="${TEST_MONGO_HOST:-mongo-test}"
REDIS_HOST="${TEST_REDIS_HOST:-redis-test}"
BACKEND_HOST="${TEST_BACKEND_HOST:-backend-test}"
FRONTEND_HOST="${TEST_FRONTEND_HOST:-frontend-test}"

MAX_WAIT=300  # 5 minutes max wait
SLEEP_INTERVAL=5

# Wait for database services
wait_for_port() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    local waited=0
    
    echo -n "⏳ Waiting for $service_name ($host:$port)... "
    
    while [ $waited -lt $MAX_WAIT ]; do
        if timeout 3 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
            echo "✅ Ready"
            return 0
        fi
        
        sleep $SLEEP_INTERVAL
        waited=$((waited + SLEEP_INTERVAL))
        echo -n "."
    done
    
    echo "❌ Timeout after ${MAX_WAIT}s"
    return 1
}

# Wait for HTTP services
wait_for_http() {
    local url="$1"
    local service_name="$2"
    local waited=0
    
    echo -n "⏳ Waiting for $service_name ($url)... "
    
    while [ $waited -lt $MAX_WAIT ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ Ready"
            return 0
        fi
        
        sleep $SLEEP_INTERVAL
        waited=$((waited + SLEEP_INTERVAL))
        echo -n "."
    done
    
    echo "❌ Timeout after ${MAX_WAIT}s"
    return 1
}

echo "📊 Database Services:"
wait_for_port "$POSTGRES_HOST" "5432" "PostgreSQL Test"
wait_for_port "$MONGO_HOST" "27017" "MongoDB Test"  
wait_for_port "$REDIS_HOST" "6379" "Redis Test"

echo ""
echo "🌐 Application Services:"
wait_for_http "http://$BACKEND_HOST:8000/health/" "Backend Test"
wait_for_http "http://$FRONTEND_HOST:3000" "Frontend Test"

echo ""
echo "🎉 All test services are ready!"
echo "Proceeding with test execution..."