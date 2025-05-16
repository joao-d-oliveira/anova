from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

class PathMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle base path prefixes in different environments.
    This ensures static files and routes work both locally and in ECS.
    """
    def __init__(self, app):
        super().__init__(app)
        # Log environment information at startup
        self.root_path = os.getenv("ROOT_PATH", "")
        logger.info(f"PathMiddleware initialized with ROOT_PATH='{self.root_path}'")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
        
        # Log important directories
        root = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(root, "/../templates")
        static_dir = os.path.join(root, "/../static")
        
        logger.info(f"Templates directory: {templates_dir}")
        logger.info(f"Templates directory exists: {os.path.exists(templates_dir)}")
        logger.info(f"Static directory: {static_dir}")
        logger.info(f"Static directory exists: {os.path.exists(static_dir)}")
    
    async def dispatch(self, request: Request, call_next):
        # Get the root_path from environment or use default empty string
        root_path = self.root_path
        
        # Get request ID from auth middleware if available
        request_id = getattr(request.state, "request_id", "no-id")
        
        # Log the request path
        logger.info(f"[{request_id}] PathMiddleware processing: {request.url.path}")
        logger.info(f"[{request_id}] Using root_path: '{root_path}'")
        
        # Store the root_path in request state for use in templates
        request.state.root_path = root_path
        
        # Log the full URL with root_path applied
        if root_path:
            logger.info(f"[{request_id}] Full URL with root_path: {root_path}{request.url.path}")
        
        # Continue processing the request
        response = await call_next(request)
        
        # Log the response status
        logger.info(f"[{request_id}] PathMiddleware response status: {response.status_code}")
        
        return response
