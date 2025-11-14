"""
Development middleware for local environment
"""
import logging

logger = logging.getLogger(__name__)


class LocalDevMiddleware:
    """
    Development middleware for additional debugging and local development features
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Add development headers
        response = self.get_response(request)
        
        # Add debug headers in development
        response['X-Dev-Environment'] = 'local'
        response['X-Debug-Mode'] = 'true'
        
        return response


# Export the middleware class
local_dev_middleware = LocalDevMiddleware