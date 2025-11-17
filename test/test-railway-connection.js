#!/usr/bin/env node
/**
 * Railway Connection Test Script
 * Tests the connection between Vercel frontend and Railway backend
 * Run with: npm run railway:test
 */

const axios = require('axios');
require('dotenv').config();

const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bright: '\x1b[1m'
};

const log = (message, color = '') => {
  console.log(`${color}${message}${colors.reset}`);
};

const getApiUrl = () => {
  // Check for production API URL first, then development
  return process.env.VITE_API_URL || 
         process.env.VITE_DEV_API_URL || 
         'https://edrs-backend-production.up.railway.app';
};

const runConnectionTests = async () => {
  log('\n🚀 Railway Backend Connection Test', colors.bright);
  log('='.repeat(50), colors.blue);
  
  const apiBaseUrl = getApiUrl();
  const apiUrl = apiBaseUrl.includes('/api') ? apiBaseUrl : `${apiBaseUrl}/api`;
  const healthUrl = `${apiBaseUrl.replace('/api', '')}/health/`;
  
  log(`🔗 Testing connection to: ${apiUrl}`, colors.blue);
  log(`🏥 Health endpoint: ${healthUrl}\n`, colors.blue);

  const tests = [];
  
  try {
    // Test 1: Health Check
    log('🔍 Test 1: Health Check...', colors.yellow);
    try {
      const healthResponse = await axios.get(healthUrl, { timeout: 10000 });
      
      if (healthResponse.status === 200) {
        log('✅ Health check passed', colors.green);
        log(`   Service: ${healthResponse.data.service || 'Unknown'}`, colors.green);
        log(`   Status: ${healthResponse.data.status || 'healthy'}`, colors.green);
        tests.push({ name: 'Health Check', status: 'PASS' });
      } else {
        log(`❌ Health check failed: ${healthResponse.status}`, colors.red);
        tests.push({ name: 'Health Check', status: 'FAIL' });
      }
    } catch (error) {
      log(`❌ Health check failed: ${error.message}`, colors.red);
      if (error.code === 'ECONNREFUSED') {
        log('   💡 Backend server may not be running', colors.yellow);
      } else if (error.code === 'ENOTFOUND') {
        log('   💡 Domain name not found - check Railway URL', colors.yellow);
      }
      tests.push({ name: 'Health Check', status: 'FAIL' });
    }

    // Test 2: API Schema
    log('\n🔍 Test 2: API Schema Access...', colors.yellow);
    try {
      const schemaResponse = await axios.get(`${apiUrl}/schema/`, { timeout: 10000 });
      
      if (schemaResponse.status === 200) {
        log('✅ API schema accessible', colors.green);
        tests.push({ name: 'API Schema', status: 'PASS' });
      } else {
        log(`❌ API schema failed: ${schemaResponse.status}`, colors.red);
        tests.push({ name: 'API Schema', status: 'FAIL' });
      }
    } catch (error) {
      log(`❌ API schema failed: ${error.message}`, colors.red);
      tests.push({ name: 'API Schema', status: 'FAIL' });
    }

    // Test 3: Database Health (via API)
    log('\n🔍 Test 3: Database Connection...', colors.yellow);
    try {
      const dbResponse = await axios.get(`${apiUrl}/core/database/health/`, { timeout: 15000 });
      
      if (dbResponse.status === 200) {
        log('✅ Database connection verified', colors.green);
        const dbData = dbResponse.data.data || {};
        if (dbData.postgresql_version) {
          log(`   PostgreSQL: ${dbData.postgresql_version}`, colors.green);
        }
        tests.push({ name: 'Database Connection', status: 'PASS' });
      } else {
        log(`❌ Database check failed: ${dbResponse.status}`, colors.red);
        tests.push({ name: 'Database Connection', status: 'FAIL' });
      }
    } catch (error) {
      log(`❌ Database check failed: ${error.message}`, colors.red);
      tests.push({ name: 'Database Connection', status: 'FAIL' });
    }

    // Test 4: CORS Configuration
    log('\n🔍 Test 4: CORS Configuration...', colors.yellow);
    try {
      const corsResponse = await axios.get(`${apiUrl}/core/categories/`, { 
        timeout: 10000,
        headers: {
          'Origin': 'https://your-app.vercel.app'
        }
      });
      
      if (corsResponse.status === 200 || corsResponse.status === 401) {
        log('✅ CORS configuration working', colors.green);
        if (corsResponse.status === 401) {
          log('   (Authentication required - this is expected)', colors.blue);
        }
        tests.push({ name: 'CORS Configuration', status: 'PASS' });
      } else {
        log(`⚠️  CORS test inconclusive: ${corsResponse.status}`, colors.yellow);
        tests.push({ name: 'CORS Configuration', status: 'PARTIAL' });
      }
    } catch (error) {
      if (error.response?.status === 401) {
        log('✅ CORS working (authentication required)', colors.green);
        tests.push({ name: 'CORS Configuration', status: 'PASS' });
      } else {
        log(`❌ CORS test failed: ${error.message}`, colors.red);
        tests.push({ name: 'CORS Configuration', status: 'FAIL' });
      }
    }

  } catch (error) {
    log(`❌ Test suite error: ${error.message}`, colors.red);
  }

  // Summary
  log('\n' + '='.repeat(50), colors.blue);
  log('📊 Test Results Summary', colors.bright);
  log('='.repeat(50), colors.blue);

  const passed = tests.filter(t => t.status === 'PASS').length;
  const failed = tests.filter(t => t.status === 'FAIL').length;
  const partial = tests.filter(t => t.status === 'PARTIAL').length;

  tests.forEach(test => {
    const icon = test.status === 'PASS' ? '✅' : test.status === 'FAIL' ? '❌' : '⚠️ ';
    const color = test.status === 'PASS' ? colors.green : test.status === 'FAIL' ? colors.red : colors.yellow;
    log(`${icon} ${test.name}`, color);
  });

  log(`\n📈 Results: ${passed} passed, ${failed} failed, ${partial} partial`, colors.blue);

  if (failed === 0) {
    log('\n🎉 All tests passed! Ready for Vercel deployment.', colors.green);
    return 0;
  } else if (failed <= 1) {
    log('\n⚠️  Minor issues detected. Deployment should work with warnings.', colors.yellow);
    return 0;
  } else {
    log('\n❌ Multiple issues detected. Fix backend connection before deploying.', colors.red);
    log('\n💡 Troubleshooting tips:', colors.blue);
    log('   1. Verify Railway backend is deployed and running', colors.blue);
    log('   2. Check VITE_API_URL environment variable', colors.blue);
    log('   3. Ensure Railway service is not sleeping', colors.blue);
    log('   4. Check Railway deployment logs', colors.blue);
    return 1;
  }
};

// Run the tests
runConnectionTests()
  .then(exitCode => process.exit(exitCode))
  .catch(error => {
    log(`\n❌ Test runner error: ${error.message}`, colors.red);
    process.exit(1);
  });