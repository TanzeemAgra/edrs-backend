# EDRS Test Environment

## 🧪 Complete Isolated Test Environment

This folder contains a comprehensive test environment that provides complete isolation from development and production environments using smart Docker techniques.

## 📁 Structure

```
test/
├── docker-compose.test.yml      # Test Docker orchestration
├── .env.test                    # Test environment variables
├── Dockerfile.backend.test      # Backend test container
├── Dockerfile.frontend.test     # Frontend test container  
├── Dockerfile.test-runner       # Test orchestration container
├── test-manager.py              # Test environment manager
├── validate_test_env.py         # Environment validator
├── TEST_ENVIRONMENT_GUIDE.md    # Comprehensive guide
├── scripts/                     # Test automation scripts
│   ├── health_check.sh          # Service health validation
│   ├── wait_for_services.sh     # Service readiness waiter
│   ├── run_backend_tests.sh     # Backend test runner
│   └── run_frontend_tests.sh    # Frontend test runner
├── diagnose_api.py              # API diagnostic tool
├── test_railway_backend.py      # Railway backend connectivity tests
├── test_system.py               # System integration tests
├── validate_database.py         # Database validation tests
├── validate_dual_database.py    # Dual database setup tests
├── start_dev_server.py          # Development server starter
├── test_login.html              # Login functionality test page
├── test_upload.html             # File upload test page
├── test_pid_document.txt        # Sample P&ID document for testing
├── reports/                     # Generated test reports (created during tests)
└── logs/                        # Test execution logs (created during tests)
```

## 🚀 Quick Start

### 1. Validate Environment
```bash
python validate_test_env.py
```

### 2. Setup Test Environment
```bash
python test-manager.py setup
```

### 3. Build and Run Tests
```bash
python test-manager.py build
python test-manager.py start
python test-manager.py test
```

## 🔒 Smart Isolation Features

- **Network Isolation**: Dedicated `edrs_test_network` (172.25.0.0/16)
- **Port Separation**: Test ports (3002, 8002, 5434, 27019, 6381)
- **Data Isolation**: Ephemeral test databases
- **Container Isolation**: Test-specific Docker images

## 📊 Test Coverage

- ✅ **Backend Tests**: Django unit, API, database, security, performance
- ✅ **Frontend Tests**: React unit, component, integration, E2E, accessibility
- ✅ **Integration Tests**: Full-stack workflow validation
- ✅ **Performance Tests**: Load testing and optimization
- ✅ **Security Tests**: Authentication and authorization
- ✅ **Database Tests**: PostgreSQL and MongoDB integration

## 📚 Documentation

For complete documentation, see: [TEST_ENVIRONMENT_GUIDE.md](TEST_ENVIRONMENT_GUIDE.md)

## 🔧 Key Commands

```bash
# Environment Management
python test-manager.py setup          # Initialize test environment
python test-manager.py build          # Build test containers
python test-manager.py start          # Start test services
python test-manager.py stop           # Stop test services

# Testing  
python test-manager.py test           # Run full test suite
python test-manager.py test --test-suite backend     # Backend only
python test-manager.py test --test-suite frontend    # Frontend only

# Monitoring
python test-manager.py status         # Service status
python test-manager.py logs           # View logs
python test-manager.py urls           # Show test URLs

# Maintenance
python test-manager.py clean          # Complete cleanup
python test-manager.py reset          # Reset test data
```

## 🌐 Test URLs

When running:
- **Frontend**: http://localhost:3002
- **Backend**: http://localhost:8002  
- **API Docs**: http://localhost:8002/api/docs/
- **Health Check**: http://localhost:8002/health/

## ✅ Benefits

- 🔒 **Complete isolation** from dev/production
- 🧪 **Comprehensive testing** across all components
- 📊 **Detailed reporting** with coverage analysis
- 🚀 **CI/CD ready** for automated pipelines
- 🛠️ **Easy management** with simple Python scripts
- 📈 **Performance optimized** containers and execution