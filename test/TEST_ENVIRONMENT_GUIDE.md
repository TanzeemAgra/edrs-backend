# EDRS Test Environment Guide

## 🧪 Isolated Test Environment

This test environment provides complete isolation from development and production environments using smart Docker techniques.

## 🔒 Smart Isolation Features

- **Separate Network**: `edrs_test_network` (172.25.0.0/16)
- **Dedicated Ports**: No conflicts with dev (3001, 8001) or prod
- **Isolated Data**: Ephemeral test databases with test data
- **Test Containers**: Specialized Docker images for testing

## 📊 Test Environment Ports

| Service    | Test Port | Dev Port | Production |
|------------|-----------|----------|------------|
| Frontend   | 3002      | 3001     | 80/443     |
| Backend    | 8002      | 8001     | 8000       |
| PostgreSQL | 5434      | 5433     | 5432       |
| MongoDB    | 27019     | 27018    | 27017      |
| Redis      | 6381      | 6380     | 6379       |

## 🚀 Quick Start

### 1. Setup Test Environment
```bash
cd test/
python test-manager.py setup
```

### 2. Build Test Services
```bash
python test-manager.py build
```

### 3. Start Test Environment  
```bash
python test-manager.py start
```

### 4. Run Comprehensive Tests
```bash
# Full test suite
python test-manager.py test

# Specific test suites
python test-manager.py test --test-suite backend
python test-manager.py test --test-suite frontend
python test-manager.py test --test-suite integration
python test-manager.py test --test-suite performance
```

### 5. View Test URLs
```bash
python test-manager.py urls
```

### 6. Clean Test Environment
```bash
python test-manager.py clean
```

## 🧪 Test Suite Components

### Backend Tests (`Dockerfile.backend.test`)
- **Unit Tests**: Django model and utility testing
- **API Tests**: REST API endpoint validation
- **Database Tests**: PostgreSQL and MongoDB integration
- **Security Tests**: Authentication and authorization
- **Performance Tests**: Response time baselines
- **Coverage Reports**: HTML coverage analysis

### Frontend Tests (`Dockerfile.frontend.test`)
- **Unit Tests**: Component logic with Vitest
- **Component Tests**: React Testing Library
- **Integration Tests**: API integration testing
- **E2E Tests**: Full user workflow testing
- **Accessibility Tests**: WCAG compliance
- **Performance Tests**: Core Web Vitals

### Integration Tests
- **API Integration**: Backend-Frontend communication
- **Database Integration**: Cross-database transactions
- **External Services**: Third-party API testing
- **Workflow Tests**: Complete user scenarios

### Performance Tests
- **Load Testing**: Concurrent user simulation
- **Stress Testing**: System limit identification
- **Database Performance**: Query optimization
- **Frontend Performance**: Bundle size and loading

## 📊 Test Reports

All test reports are generated in the `test/reports/` directory:

```
test/reports/
├── backend/
│   ├── coverage/           # HTML coverage reports
│   ├── unit_tests.log      # Unit test results
│   ├── api_tests.log       # API test results
│   └── summary.json        # Backend test summary
├── frontend/
│   ├── coverage/           # Frontend coverage
│   ├── e2e_tests.log       # E2E test results
│   └── summary.json        # Frontend test summary
├── integration/
│   └── integration.log     # Integration test results
└── performance/
    └── performance.log     # Performance test results
```

## 🔧 Test Environment Management

### Test Manager Commands

```bash
# Setup and Configuration
python test-manager.py setup          # Initialize test environment
python test-manager.py build          # Build test containers
python test-manager.py start          # Start test services
python test-manager.py stop           # Stop test services
python test-manager.py restart        # Restart test services

# Testing and Monitoring
python test-manager.py test           # Run full test suite
python test-manager.py status         # Show service status
python test-manager.py logs           # View service logs
python test-manager.py urls           # Display test URLs

# Maintenance
python test-manager.py reset          # Reset test data
python test-manager.py clean          # Complete cleanup
```

### Service-Specific Operations

```bash
# Build specific service
python test-manager.py build --service backend-test

# View specific service logs
python test-manager.py logs --service frontend-test --follow

# Run specific test category
python test-manager.py test --test-suite integration
```

## 🌐 Test Environment URLs

When the test environment is running:

- **Frontend**: http://localhost:3002
- **Backend**: http://localhost:8002
- **API Documentation**: http://localhost:8002/api/docs/
- **Admin Interface**: http://localhost:8002/admin/
- **Health Check**: http://localhost:8002/health/

## 🔒 Security and Isolation

### Network Isolation
- Test network: `172.25.0.0/16` 
- Development network: `172.20.0.0/16`
- Production uses standard Docker networks
- Complete network separation prevents any cross-contamination

### Data Isolation  
- Ephemeral test databases (destroyed after tests)
- Test-specific credentials and secrets
- No shared volumes with development or production
- Automated cleanup after test execution

### Port Isolation
- Test services use dedicated port ranges
- No conflicts with running development services  
- Easy identification of test vs dev services
- Safe parallel execution with development

## 🚀 CI/CD Integration

The test environment is designed for CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Run EDRS Test Suite
  run: |
    cd test/
    python test-manager.py setup
    python test-manager.py build
    python test-manager.py start
    python test-manager.py test
    python test-manager.py clean
```

## 🐳 Docker Test Architecture

### Test-Specific Containers

1. **Backend Test Container** (`Dockerfile.backend.test`)
   - Django with test settings
   - pytest and coverage tools
   - Test data fixtures
   - Automated test execution

2. **Frontend Test Container** (`Dockerfile.frontend.test`)
   - React with Vitest
   - Testing Library and E2E tools
   - Performance testing utilities
   - Accessibility validation

3. **Test Runner Container** (`Dockerfile.test-runner`)
   - Orchestrates all test suites
   - Generates consolidated reports
   - Manages test execution flow
   - Health monitoring and validation

4. **Database Test Containers**
   - PostgreSQL with test configuration
   - MongoDB with test data
   - Redis for test caching
   - Ephemeral data storage

## 🔍 Monitoring and Debugging

### Health Checks
All test services include comprehensive health checks:
- Database connectivity validation
- API endpoint availability
- Frontend application loading
- Service dependency verification

### Logging
Structured logging for all test components:
- Application logs in `test/logs/`
- Docker container logs via `docker-compose logs`
- Test execution logs in `test/reports/`
- Health check logs for debugging

### Debugging Failed Tests
```bash
# View specific service logs
python test-manager.py logs --service backend-test --follow

# Check service health
docker-compose -f docker-compose.test.yml exec backend-test python manage.py check

# Manual test execution
docker-compose -f docker-compose.test.yml exec backend-test bash
```

## 📈 Performance Optimization

### Test Execution Optimization
- Parallel test execution where possible
- Database connection pooling for tests
- Shared test fixtures and data
- Incremental testing support

### Resource Management
- Memory limits on test containers
- CPU allocation for optimal performance
- Cleanup automated test data
- Efficient Docker layer caching

## 🔄 Maintenance and Updates

### Regular Maintenance
```bash
# Clean old test data
python test-manager.py clean

# Update test containers  
python test-manager.py build --no-cache

# Reset test environment
python test-manager.py reset
```

### Test Environment Updates
1. Update test configurations in `.env.test`
2. Modify Docker compose for new services
3. Update test scripts in `scripts/` directory
4. Rebuild containers with `python test-manager.py build`

## 🚨 Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check if ports are in use
netstat -an | grep :8002
netstat -an | grep :3002

# Stop conflicting services
python test-manager.py stop
```

**Service Not Starting**
```bash
# Check service logs
python test-manager.py logs --service backend-test

# Verify health
python test-manager.py status
```

**Test Failures**
```bash
# Check test reports
ls -la test/reports/

# Run specific test category
python test-manager.py test --test-suite backend
```

**Database Issues**
```bash
# Reset test databases
python test-manager.py reset

# Check database connectivity
docker-compose -f docker-compose.test.yml exec postgres-test pg_isready
```

## 📝 Contributing to Tests

### Adding New Tests
1. Create test files in appropriate directories
2. Update test scripts in `test/scripts/`
3. Modify Docker configurations if needed
4. Update this documentation

### Test Best Practices
- Use descriptive test names
- Include test data setup and teardown
- Mock external dependencies
- Test both success and failure scenarios
- Include performance assertions where relevant

---

## 🎯 Benefits of This Smart Test Environment

✅ **Complete Isolation**: No impact on development or production  
✅ **Comprehensive Coverage**: Backend, Frontend, Integration, Performance  
✅ **Automated Execution**: One command runs entire test suite  
✅ **Detailed Reports**: HTML reports with coverage analysis  
✅ **CI/CD Ready**: Designed for automated pipeline integration  
✅ **Easy Management**: Simple Python script for all operations  
✅ **Resource Efficient**: Optimized containers and cleanup  
✅ **Scalable Architecture**: Easy to add new test categories