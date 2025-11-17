// Simple mock API for EDRS login - Temporary solution
// This can be deployed to Vercel as a serverless function

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { pathname } = new URL(req.url, `http://${req.headers.host}`);
  
  // Health check endpoint
  if (pathname === '/api/health' || pathname === '/health') {
    return res.status(200).json({
      status: 'healthy',
      service: 'EDRS Mock Backend API',
      version: '1.0.0'
    });
  }

  // Login endpoint
  if (pathname === '/api/auth/login' && req.method === 'POST') {
    const { email, password } = req.body;
    
    // Check for the specific user credentials
    if (email === 'tanzeem@rejlers.ae' && password === 'rejlers2025') {
      return res.status(200).json({
        user: {
          id: 2,
          username: 'tanzeem@rejlers.ae',
          email: 'tanzeem@rejlers.ae',
          first_name: 'Tanzeem',
          last_name: 'Ahmed',
          full_name: 'Tanzeem Ahmed'
        },
        token: 'mock-jwt-token-for-temporary-use',
        refresh_token: 'mock-refresh-token',
        message: 'Login successful (mock backend)'
      });
    } else {
      return res.status(401).json({
        error: 'Invalid credentials',
        message: 'Please check your email and password'
      });
    }
  }

  // Default response for unknown endpoints
  return res.status(404).json({
    error: 'Endpoint not found',
    message: 'This is a temporary mock backend for EDRS login'
  });
}