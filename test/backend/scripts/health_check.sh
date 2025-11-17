#!/bin/bash
# EDRS Test Service Health Checker
# Verifies all test services are running correctly

set -e

echo "🔍 EDRS Test Environment Health Check"
echo "======================================"

# Service endpoints
BACKEND_URL="${TEST_BACKEND_URL:-http://backend-test:8000}"
FRONTEND_URL="${TEST_FRONTEND_URL:-http://frontend-test:3000}"
POSTGRES_HOST="${TEST_POSTGRES_HOST:-postgres-test}"
MONGO_HOST="${TEST_MONGO_HOST:-mongo-test}"
REDIS_HOST="${TEST_REDIS_HOST:-redis-test}"

# Health check function
check_service() {
    local service_name="$1"
    local url="$2"
    local max_attempts="${3:-30}"
    local attempt=0
    
    echo -n "🔍 Checking $service_name... "
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ Healthy"
            return 0
        fi
        
        ((attempt++))
        sleep 2
        echo -n "."
    done
    
    echo "❌ Failed after $max_attempts attempts"
    return 1
}

# Database health check function  
check_database() {
    local db_type="$1"
    local host="$2" 
    local port="$3"
    local max_attempts="${4:-15}"
    local attempt=0
    
    echo -n "🔍 Checking $db_type at $host:$port... "
    
    while [ $attempt -lt $max_attempts ]; do
        case "$db_type" in
            "PostgreSQL")
                if pg_isready -h "$host" -p "$port" > /dev/null 2>&1; then
                    echo "✅ Ready"
                    return 0
                fi
                ;;
            "MongoDB")
                if timeout 5 bash -c "</dev/tcp/$host/$port" > /dev/null 2>&1; then
                    echo "✅ Ready"
                    return 0
                fi
                ;;
            "Redis")
                if timeout 5 bash -c "</dev/tcp/$host/$port" > /dev/null 2>&1; then
                    echo "✅ Ready"
                    return 0
                fi
                ;;
        esac
        
        ((attempt++))
        sleep 2
        echo -n "."
    done
    
    echo "❌ Failed after $max_attempts attempts"
    return 1
}

# Main health checks
echo "📊 Database Health Checks:"
check_database "PostgreSQL" "$POSTGRES_HOST" "5432"
check_database "MongoDB" "$MONGO_HOST" "27017"
check_database "Redis" "$REDIS_HOST" "6379"

echo ""
echo "🌐 Service Health Checks:"
check_service "Backend" "$BACKEND_URL/health/"
check_service "Frontend" "$FRONTEND_URL"

echo ""
echo "🎉 All test services are healthy!"
echo "Ready for comprehensive testing!"