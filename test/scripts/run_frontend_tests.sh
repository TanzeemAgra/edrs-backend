#!/bin/bash  
# EDRS Frontend Test Runner
# Comprehensive React frontend testing

set -e

echo "🎨 Running EDRS Frontend Tests"
echo "=============================="

# Configuration
FRONTEND_URL="${TEST_FRONTEND_URL:-http://frontend-test:3000}"
REPORTS_DIR="/reports/frontend"

# Ensure reports directory exists
mkdir -p "$REPORTS_DIR"

# Change to frontend directory
cd /app

# Unit Tests with Vitest
echo "📝 Unit Tests (Vitest)..."
if npm run test:unit -- --reporter=verbose --reporter=json \
   --outputFile="$REPORTS_DIR/unit_tests.json" \
   > "$REPORTS_DIR/unit_tests.log" 2>&1; then
    echo "✅ Unit tests passed"
else
    echo "❌ Unit tests failed - check $REPORTS_DIR/unit_tests.log"
    return 1
fi

# Component Tests with Testing Library
echo "🧩 Component Tests..."
if npm run test:components -- --passWithNoTests \
   --outputFile="$REPORTS_DIR/component_tests.json" \
   > "$REPORTS_DIR/component_tests.log" 2>&1; then
    echo "✅ Component tests passed"
else
    echo "❌ Component tests failed - check $REPORTS_DIR/component_tests.log"
    return 1
fi

# Integration Tests  
echo "🔗 Integration Tests..."
if npm run test:integration -- --passWithNoTests \
   --outputFile="$REPORTS_DIR/integration_tests.json" \
   > "$REPORTS_DIR/integration_tests.log" 2>&1; then
    echo "✅ Integration tests passed"
else
    echo "❌ Integration tests failed - check $REPORTS_DIR/integration_tests.log"
    return 1
fi

# E2E Tests with Playwright/Cypress
echo "🌐 End-to-End Tests..."
if npm run test:e2e -- --reporter=json \
   --outputFile="$REPORTS_DIR/e2e_tests.json" \
   > "$REPORTS_DIR/e2e_tests.log" 2>&1; then
    echo "✅ E2E tests passed"
else
    echo "❌ E2E tests failed - check $REPORTS_DIR/e2e_tests.log"
    return 1
fi

# Accessibility Tests
echo "♿ Accessibility Tests..."
if npm run test:a11y -- --outputFile="$REPORTS_DIR/a11y_tests.json" \
   > "$REPORTS_DIR/a11y_tests.log" 2>&1; then
    echo "✅ Accessibility tests passed"
else
    echo "❌ Accessibility tests failed - check $REPORTS_DIR/a11y_tests.log"
    return 1
fi

# Performance Tests  
echo "⚡ Performance Tests..."
if npm run test:performance -- --outputFile="$REPORTS_DIR/perf_tests.json" \
   > "$REPORTS_DIR/perf_tests.log" 2>&1; then
    echo "✅ Performance tests passed"
else
    echo "❌ Performance tests failed - check $REPORTS_DIR/perf_tests.log"
    return 1
fi

# Generate coverage report
echo "📊 Generating Coverage Report..."
npm run test:coverage -- --reporter=html \
  --outputDir="$REPORTS_DIR/coverage" \
  > "$REPORTS_DIR/coverage.log" 2>&1

# Generate test report
echo "📊 Generating Frontend Test Report..."
node -e "
const fs = require('fs');
const path = require('path');

const report = {
    timestamp: new Date().toISOString(),
    environment: 'test',
    frontend_tests: {
        unit_tests: 'passed',
        component_tests: 'passed', 
        integration_tests: 'passed',
        e2e_tests: 'passed',
        accessibility_tests: 'passed',
        performance_tests: 'passed'
    },
    coverage_report: '/reports/frontend/coverage/index.html',
    status: 'success'
};

fs.writeFileSync('/reports/frontend/summary.json', JSON.stringify(report, null, 2));
"

echo "🎉 Frontend Tests Complete!"
echo "📊 Reports available in: $REPORTS_DIR"