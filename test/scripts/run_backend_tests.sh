#!/bin/bash
# EDRS Backend Test Runner
# Comprehensive Django backend testing

set -e

echo "🔧 Running EDRS Backend Tests"
echo "============================="

# Configuration
BACKEND_URL="${TEST_BACKEND_URL:-http://backend-test:8000}"
REPORTS_DIR="/reports/backend"
TEST_DB_NAME="${TEST_POSTGRES_DB:-edrs_test}"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Backend test categories
echo "🧪 Running Django Test Suite..."

# Unit Tests
echo "📝 Unit Tests..."
if python manage.py test --settings=core.settings.test --verbosity=2 \
   --pattern="test_*.py" --keepdb \
   --with-coverage --cover-package=. \
   --cover-html --cover-html-dir="$REPORTS_DIR/coverage" \
   > "$REPORTS_DIR/unit_tests.log" 2>&1; then
    echo "✅ Unit tests passed"
else
    echo "❌ Unit tests failed - check $REPORTS_DIR/unit_tests.log"
    return 1
fi

# API Tests
echo "🔌 API Integration Tests..."
if python manage.py test tests.test_api --settings=core.settings.test \
   --verbosity=2 --keepdb \
   > "$REPORTS_DIR/api_tests.log" 2>&1; then
    echo "✅ API tests passed"
else
    echo "❌ API tests failed - check $REPORTS_DIR/api_tests.log"
    return 1
fi

# Database Tests
echo "💾 Database Integration Tests..."
if python manage.py test tests.test_models --settings=core.settings.test \
   --verbosity=2 --keepdb \
   > "$REPORTS_DIR/db_tests.log" 2>&1; then
    echo "✅ Database tests passed"
else
    echo "❌ Database tests failed - check $REPORTS_DIR/db_tests.log"
    return 1
fi

# Security Tests  
echo "🔒 Security Tests..."
if python manage.py test tests.test_security --settings=core.settings.test \
   --verbosity=2 --keepdb \
   > "$REPORTS_DIR/security_tests.log" 2>&1; then
    echo "✅ Security tests passed"
else
    echo "❌ Security tests failed - check $REPORTS_DIR/security_tests.log"  
    return 1
fi

# Performance baseline
echo "⚡ Performance Baseline Tests..."
if python manage.py test tests.test_performance --settings=core.settings.test \
   --verbosity=2 --keepdb \
   > "$REPORTS_DIR/performance_tests.log" 2>&1; then
    echo "✅ Performance baseline tests passed"
else
    echo "❌ Performance tests failed - check $REPORTS_DIR/performance_tests.log"
    return 1
fi

# Generate test report
echo "📊 Generating Backend Test Report..."
python -c "
import json
import datetime

report = {
    'timestamp': datetime.datetime.now().isoformat(),
    'environment': 'test',
    'backend_tests': {
        'unit_tests': 'passed',
        'api_tests': 'passed', 
        'database_tests': 'passed',
        'security_tests': 'passed',
        'performance_tests': 'passed'
    },
    'coverage_report': '/reports/backend/coverage/index.html',
    'status': 'success'
}

with open('/reports/backend/summary.json', 'w') as f:
    json.dump(report, f, indent=2)
"

echo "🎉 Backend Tests Complete!"
echo "📊 Reports available in: $REPORTS_DIR"