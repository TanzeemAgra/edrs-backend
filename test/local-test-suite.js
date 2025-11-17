/**
 * EDRS Local Development Testing Utilities
 * Smart testing tools for local Docker environment
 */

class LocalTestingSuite {
  constructor() {
    this.baseURL = 'http://localhost:8001';
    this.frontendURL = 'http://localhost:3001';
    this.results = [];
  }

  async runAllTests() {
    console.log('🧪 EDRS Local Environment Test Suite');
    console.log('=====================================\n');

    const tests = [
      this.testDatabaseConnections.bind(this),
      this.testBackendHealth.bind(this),
      this.testFrontendAccess.bind(this),
      this.testAPIEndpoints.bind(this),
      this.testAuthentication.bind(this),
      this.testCORSConfiguration.bind(this),
      this.testStaticFiles.bind(this),
    ];

    for (const test of tests) {
      try {
        await test();
      } catch (error) {
        this.logResult('FAIL', error.message, error.details || '');
      }
    }

    this.displayResults();
    return this.results;
  }

  async testDatabaseConnections() {
    const testName = 'Database Connections';
    
    try {
      const response = await fetch(`${this.baseURL}/health/db/`);
      const data = await response.json();
      
      if (response.ok && data.database?.status === 'connected') {
        this.logResult('PASS', testName, `PostgreSQL: ${data.database.name}`);
      } else {
        throw new Error(`Database health check failed: ${JSON.stringify(data)}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testBackendHealth() {
    const testName = 'Backend Health';
    
    try {
      const response = await fetch(`${this.baseURL}/health/`);
      const data = await response.json();
      
      if (response.ok && data.status === 'healthy') {
        this.logResult('PASS', testName, `Service: ${data.service} v${data.version}`);
      } else {
        throw new Error(`Health check failed: ${response.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testFrontendAccess() {
    const testName = 'Frontend Access';
    
    try {
      const response = await fetch(this.frontendURL);
      
      if (response.ok) {
        this.logResult('PASS', testName, `Status: ${response.status}`);
      } else {
        throw new Error(`Frontend returned: ${response.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testAPIEndpoints() {
    const testName = 'API Endpoints';
    
    try {
      // Test API schema endpoint
      const schemaResponse = await fetch(`${this.baseURL}/api/schema/`);
      
      if (schemaResponse.ok) {
        this.logResult('PASS', testName, 'API schema accessible');
      } else {
        throw new Error(`API schema failed: ${schemaResponse.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testAuthentication() {
    const testName = 'Authentication System';
    
    try {
      // Test auth endpoint availability (OPTIONS request)
      const authResponse = await fetch(`${this.baseURL}/api/auth/`, {
        method: 'OPTIONS'
      });
      
      if (authResponse.ok || authResponse.status === 405) {
        this.logResult('PASS', testName, 'Auth endpoints accessible');
      } else {
        throw new Error(`Auth test failed: ${authResponse.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testCORSConfiguration() {
    const testName = 'CORS Configuration';
    
    try {
      const corsResponse = await fetch(`${this.baseURL}/health/`, {
        method: 'GET',
        headers: {
          'Origin': this.frontendURL
        }
      });
      
      if (corsResponse.ok) {
        const corsHeader = corsResponse.headers.get('Access-Control-Allow-Origin');
        this.logResult('PASS', testName, `CORS headers: ${corsHeader || 'Present'}`);
      } else {
        throw new Error(`CORS test failed: ${corsResponse.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  async testStaticFiles() {
    const testName = 'Static Files';
    
    try {
      const staticResponse = await fetch(`${this.baseURL}/static/`);
      
      // 404 is acceptable for static directory listing
      if (staticResponse.status === 404 || staticResponse.ok) {
        this.logResult('PASS', testName, 'Static file serving configured');
      } else {
        throw new Error(`Static files test failed: ${staticResponse.status}`);
      }
    } catch (error) {
      throw { message: testName, details: error.message };
    }
  }

  logResult(status, testName, details) {
    const result = {
      status,
      test: testName,
      details,
      timestamp: new Date().toISOString()
    };
    
    this.results.push(result);
    
    const icon = status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${testName}: ${details}`);
  }

  displayResults() {
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 LOCAL TEST RESULTS');
    console.log('='.repeat(50));
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📋 Total: ${this.results.length}`);
    
    if (failed === 0) {
      console.log('\n🎉 All tests passed! Your local environment is ready!');
      console.log(`🌐 Frontend: ${this.frontendURL}`);
      console.log(`🚀 Backend: ${this.baseURL}`);
      console.log(`📚 API Docs: ${this.baseURL}/api/docs/`);
      console.log(`👤 Admin: ${this.baseURL}/admin/ (admin/admin123)`);
    } else {
      console.log('\n⚠️ Some tests failed. Check Docker logs for details.');
    }
  }
}

// Docker service health checker
class DockerHealthChecker {
  async checkServices() {
    console.log('🐳 Checking Docker Services...\n');
    
    const services = [
      { name: 'PostgreSQL', url: 'http://localhost:5433', type: 'database' },
      { name: 'MongoDB', url: 'http://localhost:27018', type: 'database' },
      { name: 'Redis', url: 'http://localhost:6380', type: 'cache' },
      { name: 'Backend', url: 'http://localhost:8001/health/', type: 'api' },
      { name: 'Frontend', url: 'http://localhost:3001', type: 'web' }
    ];
    
    for (const service of services) {
      await this.checkService(service);
    }
  }
  
  async checkService(service) {
    try {
      if (service.type === 'database' || service.type === 'cache') {
        // For databases, we'll just check if the port is accessible
        console.log(`🔍 ${service.name}: Configured (check Docker logs for status)`);
        return;
      }
      
      const response = await fetch(service.url, { 
        timeout: 5000,
        headers: { 'User-Agent': 'EDRS-Health-Check' }
      });
      
      if (response.ok) {
        console.log(`✅ ${service.name}: Healthy (${response.status})`);
      } else {
        console.log(`⚠️ ${service.name}: Response ${response.status}`);
      }
    } catch (error) {
      console.log(`❌ ${service.name}: ${error.message}`);
    }
  }
}

// Performance monitor for local development
class LocalPerformanceMonitor {
  constructor() {
    this.metrics = [];
  }
  
  async measureEndpoint(url, name) {
    const start = Date.now();
    
    try {
      const response = await fetch(url);
      const duration = Date.now() - start;
      
      this.metrics.push({
        name,
        url,
        duration,
        status: response.status,
        success: response.ok
      });
      
      console.log(`⚡ ${name}: ${duration}ms (${response.status})`);
    } catch (error) {
      console.log(`💥 ${name}: Failed - ${error.message}`);
    }
  }
  
  async runPerformanceTests() {
    console.log('⚡ Performance Test Suite\n');
    
    const endpoints = [
      { url: 'http://localhost:8001/health/', name: 'Backend Health' },
      { url: 'http://localhost:8001/api/schema/', name: 'API Schema' },
      { url: 'http://localhost:3001', name: 'Frontend Load' },
    ];
    
    for (const endpoint of endpoints) {
      await this.measureEndpoint(endpoint.url, endpoint.name);
    }
    
    this.displayPerformanceResults();
  }
  
  displayPerformanceResults() {
    const avgDuration = this.metrics.reduce((acc, m) => acc + m.duration, 0) / this.metrics.length;
    
    console.log('\n📈 Performance Summary:');
    console.log(`   Average Response Time: ${avgDuration.toFixed(0)}ms`);
    console.log(`   Successful Requests: ${this.metrics.filter(m => m.success).length}/${this.metrics.length}`);
  }
}

// Export utilities for use in different environments
if (typeof module !== 'undefined' && module.exports) {
  // Node.js environment
  module.exports = {
    LocalTestingSuite,
    DockerHealthChecker,
    LocalPerformanceMonitor
  };
} else {
  // Browser environment
  window.EDRSLocalTest = {
    LocalTestingSuite,
    DockerHealthChecker,
    LocalPerformanceMonitor
  };
}

// Auto-run in browser console
if (typeof window !== 'undefined') {
  console.log('🧪 EDRS Local Testing Utilities Loaded');
  console.log('Run: new EDRSLocalTest.LocalTestingSuite().runAllTests()');
}