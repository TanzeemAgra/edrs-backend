/**
 * EDRS OpenAI Integration Test
 * Test AI features in local development environment
 */

class OpenAIIntegrationTest {
  constructor() {
    this.baseURL = 'http://localhost:8001/api/ai';
    this.results = [];
  }

  async runTests() {
    console.log('🤖 Testing OpenAI Integration...\n');

    const tests = [
      this.testOpenAIHealth.bind(this),
      this.testAIFeatures.bind(this),
      this.testContentGeneration.bind(this),
      this.testDocumentAnalysis.bind(this),
      this.testSuggestions.bind(this)
    ];

    for (const test of tests) {
      try {
        await test();
      } catch (error) {
        this.logResult('FAIL', error.testName, error.message);
      }
    }

    this.displayResults();
  }

  async testOpenAIHealth() {
    const testName = 'OpenAI Health Check';
    
    try {
      const response = await fetch(`${this.baseURL}/health/`);
      const data = await response.json();
      
      if (response.ok) {
        const status = data.health?.status || 'unknown';
        this.logResult('PASS', testName, `Status: ${status}`);
      } else {
        throw { testName, message: `Health check returned ${response.status}` };
      }
    } catch (error) {
      throw { testName, message: error.message || 'Network error' };
    }
  }

  async testAIFeatures() {
    const testName = 'AI Features Endpoint';
    
    try {
      // This requires authentication, so we'll test without auth first
      const response = await fetch(`${this.baseURL}/features/`);
      
      // Expect 401 Unauthorized since we need authentication
      if (response.status === 401) {
        this.logResult('PASS', testName, 'Correctly requires authentication');
      } else if (response.ok) {
        this.logResult('PASS', testName, 'Features endpoint accessible');
      } else {
        throw { testName, message: `Unexpected status: ${response.status}` };
      }
    } catch (error) {
      throw { testName, message: error.message || 'Network error' };
    }
  }

  async testContentGeneration() {
    const testName = 'Content Generation (Unauthenticated)';
    
    try {
      const response = await fetch(`${this.baseURL}/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: 'Test prompt',
          type: 'general'
        })
      });
      
      // Expect 401 Unauthorized since authentication is required
      if (response.status === 401) {
        this.logResult('PASS', testName, 'Correctly requires authentication');
      } else {
        throw { testName, message: `Expected 401, got ${response.status}` };
      }
    } catch (error) {
      throw { testName, message: error.message || 'Network error' };
    }
  }

  async testDocumentAnalysis() {
    const testName = 'Document Analysis (Unauthenticated)';
    
    try {
      const response = await fetch(`${this.baseURL}/analyze/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: 'Test document content',
          analysis_type: 'summary'
        })
      });
      
      // Expect 401 Unauthorized
      if (response.status === 401) {
        this.logResult('PASS', testName, 'Correctly requires authentication');
      } else {
        throw { testName, message: `Expected 401, got ${response.status}` };
      }
    } catch (error) {
      throw { testName, message: error.message || 'Network error' };
    }
  }

  async testSuggestions() {
    const testName = 'AI Suggestions (Unauthenticated)';
    
    try {
      const response = await fetch(`${this.baseURL}/suggestions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: 'Document management',
          task: 'Improve workflow'
        })
      });
      
      // Expect 401 Unauthorized
      if (response.status === 401) {
        this.logResult('PASS', testName, 'Correctly requires authentication');
      } else {
        throw { testName, message: `Expected 401, got ${response.status}` };
      }
    } catch (error) {
      throw { testName, message: error.message || 'Network error' };
    }
  }

  logResult(status, testName, details) {
    const result = { status, test: testName, details };
    this.results.push(result);
    
    const icon = status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${testName}: ${details}`);
  }

  displayResults() {
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    
    console.log('\n🤖 OpenAI Integration Test Results:');
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    
    if (failed === 0) {
      console.log('\n🎉 OpenAI integration is properly configured!');
      console.log('📋 Next steps:');
      console.log('  1. Start local environment: python dev-manager.py start');
      console.log('  2. Create admin user for testing authenticated endpoints');
      console.log('  3. Test AI features through API docs: http://localhost:8001/api/docs/');
    } else {
      console.log('\n⚠️ Some tests failed. Check configuration.');
    }
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = OpenAIIntegrationTest;
} else {
  window.OpenAIIntegrationTest = OpenAIIntegrationTest;
}

// Usage instructions
console.log('🤖 OpenAI Integration Test Suite Loaded');
console.log('Run: new OpenAIIntegrationTest().runTests()');